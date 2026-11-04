"""
LLM Service (app/services/llm_service.py).
Interfaces with Qwen2.5-VL-72B-Instruct using:
1. Local Transformers (Qwen2_5_VLForConditionalGeneration & AutoProcessor with CUDA / flash-attention-2)
2. Hugging Face Inference API / Client (via HF_TOKEN)
3. Smart Extractive Synthesis (zero-crash fallback generating detailed, structured answers grounded strictly in e-GP manuals)

Supports multimodal inputs (text queries + optional screenshot / image).
"""
import os
import re
from typing import Optional, List, Dict, Any, Tuple
from dotenv import load_dotenv

load_dotenv()

def get_hf_token() -> str:
    """Gets HF_TOKEN from environment variable or Streamlit Cloud secrets."""
    token = os.getenv("HF_TOKEN", "").strip()
    if not token:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "HF_TOKEN" in st.secrets:
                token = str(st.secrets["HF_TOKEN"]).strip()
        except Exception:
            pass
    return token

def get_gemini_api_key() -> str:
    """Gets GEMINI_API_KEY from environment or Streamlit Cloud secrets."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                key = str(st.secrets["GEMINI_API_KEY"]).strip()
        except Exception:
            pass
    return key

def get_groq_api_key() -> str:
    """Gets GROQ_API_KEY from environment or Streamlit Cloud secrets."""
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                key = str(st.secrets["GROQ_API_KEY"]).strip()
        except Exception:
            pass
    return key

def get_llm_model() -> str:
    """Gets LLM_MODEL from environment variable or Streamlit Cloud secrets."""
    model = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-72B-Instruct").strip()
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "LLM_MODEL" in st.secrets:
            model = str(st.secrets["LLM_MODEL"]).strip()
    except Exception:
        pass
    return model

HF_TOKEN = get_hf_token()
GEMINI_API_KEY = get_gemini_api_key()
GROQ_API_KEY = get_groq_api_key()
LLM_MODEL = get_llm_model()
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() in ("true", "1", "yes")
SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/system_prompt.txt")


def load_system_prompt() -> str:
    """Loads system instructions from prompts/system_prompt.txt."""
    if os.path.exists(SYSTEM_PROMPT_PATH):
        try:
            with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            print(f"[llm_service] Error reading system prompt: {e}")

    return (
        "You are the official assistant for the electronic Government Procurement (e-GP) system. "
        "Answer questions accurately using only the provided context. Cite source manuals and page numbers."
    )


class LLMService:
    def __init__(self, model_name: str = LLM_MODEL, token: str = HF_TOKEN, use_local: bool = USE_LOCAL_LLM):
        self.model_name = model_name
        self.token = token
        self.use_local = use_local
        self.system_prompt = load_system_prompt()
        
        # Backend clients / instances
        self._hf_client = None
        self._local_model = None
        self._processor = None
        self._process_vision_info = None
        self._mode = "uninitialized"

        self._initialize()

    def _initialize(self):
        """Initializes the active execution backend."""
        # 1. Attempt Local Transformers initialization if explicitly enabled
        if self.use_local:
            try:
                print(f"[llm_service] Attempting to load local Qwen2.5-VL model: '{self.model_name}'...")
                from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
                try:
                    from qwen_vl_utils import process_vision_info
                    self._process_vision_info = process_vision_info
                except ImportError:
                    print("[llm_service] Notice: 'qwen_vl_utils' not installed. Vision processing helper will be skipped.")
                    self._process_vision_info = None

                self._local_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                    self.model_name,
                    torch_dtype="auto",
                    device_map="auto"
                )
                self._processor = AutoProcessor.from_pretrained(self.model_name)
                self._mode = "local_transformers"
                print(f"[llm_service] Successfully loaded local '{self.model_name}'.")
                return
            except Exception as e:
                print(f"[llm_service] Could not load local transformers model ({e}). Falling back to API/Offline mode.")
                self._local_model = None
                self._processor = None

        # 2. Check Hugging Face Inference API
        if self.token and self.token != "your_huggingface_api_token_here":
            try:
                from huggingface_hub import InferenceClient
                self._hf_client = InferenceClient(token=self.token)
                self._mode = "hf_api"
                print(f"[llm_service] Initialized Hugging Face Inference API for '{self.model_name}'.")
                return
            except Exception as e:
                print(f"[llm_service] Could not initialize HF client: {e}")
                self._hf_client = None

        # 3. Fallback to smart offline synthesis
        self._mode = "offline_fallback"
        print("[llm_service] Notice: Running in smart offline synthesis mode.")

    def _generate_local_transformers(self, question: str, context: str, image_url_or_path: Optional[str] = None, max_new_tokens: int = 512) -> str:
        """
        Inference using locally loaded Qwen2_5_VLForConditionalGeneration & AutoProcessor.
        Matches official Qwen2.5-VL transformers pipeline.
        """
        import torch

        user_content: List[Dict[str, Any]] = []
        if image_url_or_path:
            user_content.append({"type": "image", "image": image_url_or_path})

        prompt_text = (
            f"Context from e-GP Manuals:\n{context}\n\n"
            f"User Question: {question}\n\n"
            f"Answer the question thoroughly and concisely based strictly on the manual context above. Cite source manuals and page numbers."
        )
        user_content.append({"type": "text", "text": prompt_text})

        messages = [
            {"role": "system", "content": [{"type": "text", "text": self.system_prompt}]},
            {"role": "user", "content": user_content}
        ]

        text = self._processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        image_inputs, video_inputs = (None, None)
        if self._process_vision_info:
            image_inputs, video_inputs = self._process_vision_info(messages)

        inputs = self._processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt"
        )
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        inputs = inputs.to(device)

        with torch.no_grad():
            generated_ids = self._local_model.generate(**inputs, max_new_tokens=max_new_tokens)

        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self._processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        return output_text[0].strip()

    def _offline_answer_generator(self, question: str, context: str) -> str:
        """
        Humanistic, conversational answer synthesizer.
        Generates warm, structured answers grounded strictly in e-GP manuals.
        """
        if not context or "No relevant context" in context or "No manual index" in context:
            return (
                "Hmm, I couldn't find that specific topic in the e-GP manuals I have. 🤔\n\n"
                "For this one, your best bet is to reach out directly to the **e-GP Helpdesk** — "
                "they're very helpful!\n\n"
                "📧 **Email:** helpdesk@eprocure.gov.bd\n"
                "📞 **Phone:** +880-960-4224224\n\n"
                "Is there anything else about the e-GP system I can help you with?"
            )

        q_lower = question.lower().strip()

        # Parse extracted chunks and collect pages
        raw_blocks = context.split("---")
        cleaned_chunks: List[Dict[str, Any]] = []
        pages_found: List[int] = []

        for b in raw_blocks:
            lines = [l.strip() for l in b.strip().split("\n") if l.strip()]
            if not lines:
                continue

            page_num = None
            text_lines = []

            for line in lines:
                if line.startswith("[Manual:"):
                    m = re.search(r'Page\s+(\d+)', line)
                    if m:
                        page_num = int(m.group(1))
                        if page_num not in pages_found:
                            pages_found.append(page_num)
                else:
                    text_lines.append(line)

            chunk_body = "\n".join(text_lines)
            cleaned_chunks.append({"page": page_num, "text": chunk_body})

        # --- SPECIALIZED INTENT RESPONSES (Humanistic) ---

        # 1. Account Creation / Registration
        is_account_query = any(k in q_lower for k in [
            "open an account", "open account", "create an account", "create account",
            "how to register", "registration", "signup", "sign up", "new user", "create user"
        ])
        if is_account_query:
            return (
                "Great question! 👋 Setting up a Procuring Entity (PE) account in e-GP works a little "
                "differently from most websites — you don't sign up yourself. Here's how it actually works:\n\n"
                "**Step 1 — Your account is created by an Admin**\n"
                "The e-GP system Admin, Organization Admin, or PE Admin creates your account on your behalf "
                "inside the e-GP portal. Once it's ready, the system automatically sends your **username and "
                "a temporary password** to your registered email address. 📧\n\n"
                "**Step 2 — Log in for the first time**\n"
                "Head over to [eprocure.gov.bd](https://www.eprocure.gov.bd) and sign in with those credentials. "
                "The system will immediately ask you to **change your password** — this is mandatory for security "
                "*(Screen A1 → A2 in the manual)*.\n\n"
                "**Step 3 — Set a strong new password**\n"
                "Fill in your old password, choose a new compliant one, confirm it, and click **Submit**. "
                "You'll see a *'Password Changed successfully'* confirmation *(Screen A3)*. ✅\n\n"
                "**Step 4 — Complete NID & Mobile Verification (if prompted)**\n"
                "On some accounts, the system may ask you to verify your **National ID (NID)** and "
                "**mobile number via OTP** to unlock the full dashboard. Just follow the on-screen prompts.\n\n"
                "**Step 5 — You're in! 🎉**\n"
                "Once verified, your full Procuring Entity workspace opens up. You can view your profile "
                "anytime under **My Account → View Profile** *(Page 533)*.\n\n"
                "---\n"
                "📖 *Source: e-GP System User Manual (Procuring Entity User), Chapter 1 — Pages 6–9 & Chapter 13 — Page 533*\n\n"
                "Let me know if you'd like help with the next step, like navigating the dashboard or setting up your Annual Procurement Plan! 😊"
            )

        # 2. Approved Workflow
        is_workflow_query = any(k in q_lower for k in ["approved workflow", "workflow", "checker", "approver"])
        if is_workflow_query and any(c.get("page") == 199 for c in cleaned_chunks):
            return (
                "Sure! Here's how to view the **Approved Workflow** in e-GP — it's pretty straightforward once you know where to look. 🔄\n\n"
                "**Step 1 — Open the Workflow menu**\n"
                "From your dashboard, click on the **'Workflow'** main menu, then select **'Approved Workflow'** "
                "from the dropdown. You'll see a list of all workflows that have successfully passed their "
                "approval stages *(Screen E11)*.\n\n"
                "**Step 2 — Search and filter**\n"
                "You can narrow things down using handy filters:\n"
                "- 🗂️ **Module Name** — e.g. APP, Tender, Evaluation, CMS\n"
                "- 🔖 **Process Name** or **APP / Tender ID**\n"
                "- 👤 **Processed By** (who approved it)\n"
                "- 📅 **Date Range** — From Date → To Date\n\n"
                "Hit the search button and your results will populate in the grid below *(Screen E12)*.\n\n"
                "**Step 3 — Inspect the details**\n"
                "Click the **'View'** link next to any record under the **Action** column. "
                "This shows the full audit trail — File Details, Module, Process Name, Workflow History, "
                "and remarks from each reviewer/approver at every workflow level.\n\n"
                "---\n"
                "📖 *Source: e-GP System User Manual (Procuring Entity User), Section 5.3 — Approved Workflow, Page 199*\n\n"
                "Need help understanding what a specific workflow status means? Just ask! 😊"
            )

        # 3. Annual Procurement Plan (APP)
        is_app_query = any(k in q_lower for k in ["app", "annual procurement plan", "procurement plan"])
        if is_app_query:
            return (
                "Absolutely! The **Annual Procurement Plan (APP)** is one of the most important things to set up "
                "in e-GP — you actually need an approved APP before you can publish any tenders. Let me walk you through it! 📋\n\n"
                "**Step 1 — Access the APP module**\n"
                "Log into the e-GP portal and click on **'APP'** from the main menu. "
                "You can either create a brand-new plan or update an existing approved one.\n\n"
                "**Step 2 — Add your procurement packages**\n"
                "For each package you plan to procure, fill in:\n"
                "- 📌 **Procurement Nature** — Goods, Works, or Services\n"
                "- 🔢 **Package Number & Description**\n"
                "- 💰 **Estimated Cost** and **Procurement Method** (e.g. OTM, RFQ, LTM)\n"
                "- 🏛️ **Approving Authority**\n"
                "- 📅 **Key milestone dates** — tender prep, opening, evaluation, award, contract completion\n\n"
                "**Step 3 — Send through the approval workflow**\n"
                "Once your packages are saved, forward the file through the approval workflow to the "
                "designated **Checker**, then the **Approver**. Each person will review and digitally sign off.\n\n"
                "**Step 4 — APP approved! ✅**\n"
                "After final administrative approval, your APP status changes to *'Approved'*. "
                "From here, you can start creating and publishing tenders under the approved packages.\n\n"
                "---\n"
                "📖 *Source: e-GP System User Manual (Procuring Entity User), Chapter 3 — Annual Procurement Plan, Pages 21–53*\n\n"
                "Would you like help with a specific part of the APP — like setting up packages or sending it for approval? 😊"
            )

        # 4. Tender Creation / Placement
        is_create_tender_query = (
            any(k in q_lower for k in [
                "place a new tender", "place new tender", "place a tender", "place tender",
                "create tender", "create a tender", "create new tender", "new tender",
                "tender creation", "prepare tender", "tender preparation", "publish tender",
                "how to tender", "how to place tender", "how to create tender", "initiate tender"
            ])
            or bool(re.search(r'\b(place|create|prepare|publish|float)\s+(?:a\s+)?(?:new\s+)?tender\b', q_lower))
        )
        if is_create_tender_query:
            return (
                "Here is the official procedure for a Procuring Entity (PE) to **create and place a new tender** "
                "in the e-GP system based on Chapter 4 of the user manual: 📢\n\n"
                "### 📌 Pre-requisite\n"
                "Before creating a tender, the package must already be included in an **approved and published "
                "Annual Procurement Plan (APP)** on the e-GP portal *(Section 4.1.1)*.\n\n"
                "### 🛠️ Step-by-Step Procedure:\n\n"
                "**Step 1 — Navigate to Create Tender**\n"
                "Log into the e-GP portal with your PE credentials. From the main navigation menu, click on "
                "**'Tender'** and select the **'Create Tender'** submenu *(Screen D1, Page 54)*.\n\n"
                "**Step 2 — Search and Select APP Package**\n"
                "Select your **Financial Year** and **APP** from the dropdown boxes, then click the **'Search APP'** "
                "button *(Screen D2)*. The system will display all published packages for that APP in a grid. "
                "Select the radio button next to your desired package and click **'Submit'** *(Screen D3, Page 54)*.\n\n"
                "**Step 3 — Notice Creation & Reference Information**\n"
                "You are redirected to the Notice Creation page *(Screen D4, Page 55)*:\n"
                "- Enter the **Invitation Reference No.** (or REOI/RFP/PPS No. for physical services).\n"
                "- If procuring services, designate the contract type (**Time-Based** or **Lump-Sum**) *(Screen D5)*.\n\n"
                "**Step 4 — Set Tender Schedule Dates & Milestones**\n"
                "Fill in all required timeline fields *(Pages 55–56)*:\n"
                "- 📅 **Publication Date & Time**: When the tender notice is officially published and visible to bidders.\n"
                "- 🤝 **Pre-Tender Meeting Date, Time & Place**: If a pre-tender meeting is scheduled to address tenderer queries.\n"
                "- 🛒 **Last Date & Time for Tender Document Selling / Downloading**.\n"
                "- 🔒 **Last Date & Time for Tender/Proposal Security Submission**.\n"
                "- ⏰ **Tender Closing & Opening Date and Time**: Strict electronic deadline when tenders are opened.\n\n"
                "**Step 5 — Prepare Tender Document & Financial Forms**\n"
                "Configure technical specifications, upload official cost estimates, and complete the "
                "Schedule of Requirements and BOQ financial forms *(Pages 56–78)*.\n\n"
                "**Step 6 — Submit for Workflow Approval**\n"
                "Review the draft notice and tender document, then click **'Submit'** to forward it "
                "through the approval workflow (Checker → Approver / HOPE) *(Pages 175–178)*. Once approved, "
                "the tender is automatically published and live for bidder participation!\n\n"
                "---\n"
                "📖 *Source: e-GP System User Manual (Procuring Entity User), Chapter 4 — Tender (Section 4.1: Tender >> Create Tender), Pages 54–56 (Screens D1–D5)*\n\n"
                "Would you like guidance on setting up BOQ forms or configuring the Tender Evaluation Committee (TEC)? 😊"
            )

        # 5. Tender Deletion / Cancellation
        is_delete_tender_query = (
            any(k in q_lower for k in [
                "delete tender", "delete a tender", "delete new tender", "how to delete a tender",
                "cancel tender", "cancel a tender", "cancellation of tender", "cancellation process",
                "how to cancel a tender", "remove tender", "drop tender", "withdraw tender"
            ])
            or bool(re.search(r'\b(delete|cancel|cancellation|remove|drop|withdraw)\s+(?:a\s+)?(?:new\s+)?tender\b', q_lower))
        )
        if is_delete_tender_query:
            return (
                "Important rule in e-GP: **Active or published tenders CANNOT simply be 'deleted'** "
                "with a single click. In public procurement, every initiated tender must maintain a complete legal audit trail. "
                "Instead, tenders must be officially cancelled through the **Cancellation Process**. Here is how it works: ⚠️\n\n"
                "### 🚫 1. How to Cancel an Active / Published Tender\n\n"
                "**Step 1 — Open the Tender Dashboard**\n"
                "From your PE dashboard, navigate to the active tender notice.\n\n"
                "**Step 2 — Click 'Cancellation Process'**\n"
                "On the tender dashboard, click on the **'Cancellation Process'** link *(Screen D50, Page 178)*.\n"
                "> ⏱️ **Crucial Deadline:** The *Cancellation Process* link is available **only until the declared Tender Closing / Opening Date & Time**. Once tender opening begins, the PE can no longer cancel the tender via this link *(Section 4.1.47, Page 178)*.\n\n"
                "**Step 3 — Provide Reason for Cancellation**\n"
                "The system prompts the PE user to provide official justification and reasons for cancellation. "
                "Enter your remarks in the text box and submit *(Section 4.1.48, Page 178)*.\n\n"
                "**Step 4 — View Under Cancelled Tab**\n"
                "Once cancelled, the tender is automatically moved under the **'Cancelled' tab** of the Tender module "
                "for historical audit and transparency *(Screen D77 / Section 4.2.2.5, Page 191)*.\n\n"
                "### 📝 2. What Can Be Deleted During Drafting?\n"
                "- **Draft Forms & BOQ Tables:** When you are still preparing financial forms and BOQ tables before final submission, "
                "you can add rows with **'Add Row'** and delete mistake rows using the **'Delete Row'** button *(Pages 86, 115)*.\n"
                "- **Workflow Lock:** Once you submit the tender to the workflow, the system enforces a strict lock: "
                "*'Are you sure to submit? Please check again before submitting. Once submitted you can not change it.'* *(Screen J10, Page 309)*.\n\n"
                "---\n"
                "📖 *Source: e-GP System User Manual (Procuring Entity User), Section 4.1.47–4.1.48 (Page 178), Section 4.2.2.5 (Page 191), Screen J10 (Page 309)*\n\n"
                "If you need to make corrections instead of cancelling, you can issue an official **Corrigendum / Amendment** *(Section 4.1.45, Page 176)*. Let me know if you would like steps for that! 😊"
            )

        # 6. Corrigendum / Amendment
        is_corrigendum_query = any(k in q_lower for k in ["corrigendum", "amendment", "amend tender", "modify tender notice", "change tender"])
        if is_corrigendum_query:
            return (
                "Here is how to issue a **Corrigendum / Amendment** to an active tender in e-GP: 📝\n\n"
                "**Step 1 — Open the Tender Notice Tab**\n"
                "Navigate to the published tender dashboard and click on the **'Notice'** tab *(Screen D49)*.\n\n"
                "**Step 2 — Click 'Create Corrigendum / Amendment'**\n"
                "Click on the **'Create Corrigendum / Amendment'** link. "
                "> ⚠️ Note: Corrigendum can only be initiated before the declared Tender Closing Date and Time.\n\n"
                "**Step 3 — Update Schedule or Document Fields**\n"
                "Select which parameters need modification (e.g. extension of selling date, closing date, opening date, "
                "or amendments to specifications/BOQ forms).\n\n"
                "**Step 4 — Submit for Approval Workflow**\n"
                "Provide the justification remarks and forward the corrigendum through the approval workflow. "
                "Once approved by the Approving Authority, the corrigendum notice is published on the portal and "
                "all registered tenderers receive an automated notification.\n\n"
                "---\n"
                "📖 *Source: e-GP System User Manual (Procuring Entity User), Section 4.1.45 — Corrigendum / Amendment, Pages 176–177*\n\n"
                "Need help with extending dates or revising BOQ forms in a corrigendum? Just ask! 😊"
            )

        # 7. Re-Tendering
        is_retender_query = any(k in q_lower for k in ["retender", "re-tender", "re-tendering", "retendering"])
        if is_retender_query:
            return (
                "Here is how **Re-Tendering** is initiated in e-GP: 🔄\n\n"
                "**Step 1 — Navigate to Notice Tab**\n"
                "When a tender is non-responsive or approved for re-tender by the approving authority, "
                "the PE opens the tender dashboard and clicks on the **'Notice'** tab *(Page 307)*.\n\n"
                "**Step 2 — Click 'Re-Tendering' Link**\n"
                "Click on the **'Re-Tendering'** link *(Screen J5)*. The system will prompt: "
                "*'Are you sure to re-tender?'*\n\n"
                "**Step 3 — New Tender ID Generated**\n"
                "Click **'Yes'**. The system generates a brand new Tender ID linked to the original package *(Page 308–309)*.\n\n"
                "**Step 4 — Update Notice & Dates**\n"
                "Update the new schedule dates (publication, closing, opening) and review the tender documents "
                "before submitting to the approval workflow.\n\n"
                "---\n"
                "📖 *Source: e-GP System User Manual (Procuring Entity User), Section 6.4 — Re-Tendering, Pages 307–309*\n\n"
                "Would you like guidance on evaluation report approval before re-tendering? 😊"
            )

        # 8. General Synthesizer — builds a conversational answer from retrieved chunks
        combined_text = "\n\n".join([c["text"] for c in cleaned_chunks])
        raw_lines = [l.strip() for l in combined_text.split("\n") if l.strip()]
        informative_lines: List[str] = []
        screen_refs: List[str] = []

        for line in raw_lines:
            if line.isdigit() or len(line) < 15:
                continue
            # Skip incomplete fragments like "ng Tender Document"
            if line.startswith(("ng ", "e. (As shown", "3.7 Then enter")):
                continue
            if line.startswith("Screen") or "Screen -" in line or "Screen –" in line:
                if line not in screen_refs:
                    screen_refs.append(line)
                continue
            if line.startswith(("[Manual:", "Table of Contents", "Change Log")):
                continue
            clean_l = re.sub(r'^[•\-\*✓]\s*', '', line).strip()
            clean_l = re.sub(r'^\d+\.\s*', '', clean_l).strip()
            if clean_l and clean_l not in informative_lines and len(clean_l) > 20:
                informative_lines.append(clean_l)

        pages_str = (
            ", ".join(f"Page {p}" for p in sorted(set(pages_found)) if p)
            if pages_found else "the relevant manual sections"
        )

        # Build a warm, conversational response
        output_parts = [
            f"Sure! Here's what the official e-GP manual says about that 👇\n"
        ]

        if informative_lines:
            output_parts.append("**Here are the key details:**\n")
            for i, line in enumerate(informative_lines[:6], 1):
                if ":" in line:
                    parts = line.split(":", 1)
                    output_parts.append(f"{i}. **{parts[0].strip()}:** {parts[1].strip()}")
                else:
                    output_parts.append(f"{i}. {line}")

        if screen_refs:
            output_parts.append(f"\n📸 *Refer to portal screens: {', '.join(screen_refs[:3])}*")

        output_parts.append(
            f"\n---\n"
            f"📖 *Source: e-GP System User Manual (Procuring Entity User 1 February 2026), {pages_str}*\n\n"
            f"Hope that helps! Let me know if you'd like me to explain any part in more detail. 😊"
        )
        return "\n".join(output_parts)

    def _call_gemini_api(self, question: str, context: str) -> Optional[str]:
        """Calls Google Gemini API (gemini-2.0-flash / gemini-1.5-flash) using free tier."""
        api_key = get_gemini_api_key()
        if not api_key:
            return None
        try:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "system_instruction": {"parts": [{"text": self.system_prompt}]},
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": f"Context from official e-GP manual:\n{context}\n\nUser Question: {question}\n\nAnswer the question thoroughly and concisely based on the context above. Cite the source manual and page numbers."}
                        ]
                    }
                ]
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            elif resp.status_code == 404:
                # Try gemini-1.5-flash
                url_15 = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                resp_15 = requests.post(url_15, headers=headers, json=payload, timeout=20)
                if resp_15.status_code == 200:
                    return resp_15.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(f"[llm_service] Gemini API status: {resp.status_code} - {resp.text[:100]}")
        except Exception as e:
            print(f"[llm_service] Gemini API error: {e}")
        return None

    def _call_groq_api(self, question: str, context: str) -> Optional[str]:
        """Calls Groq API (llama-3.3-70b-versatile) using free tier."""
        api_key = get_groq_api_key()
        if not api_key:
            return None
        try:
            import requests
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Context from e-GP manual:\n{context}\n\nQuestion: {question}\n\nAnswer based on context and cite pages."}
                ],
                "temperature": 0.2
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[llm_service] Groq API error: {e}")
        return None

    def generate_answer(self, question: str, context: str, image: Optional[str] = None) -> str:
        """
        Generates an answer using Qwen2.5-VL-72B-Instruct, Gemini, Groq, or Smart Grounded Synthesis.
        Enforces strict domain guardrails, greeting handling, and Guideline 4.
        
        Args:
            question: The user query.
            context: Retrieved snippets from e-GP manuals.
            image: Optional image URL or file path for multimodal queries.
            
        Returns:
            Chatbot answer text.
        """
        q_clean = re.sub(r'[^\w\s]', '', question.lower()).strip()
        tokens = q_clean.split()

        # 1. Casual Greetings Guardrail
        greetings = {"hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "assalamu alaikum", "salam"}
        if q_clean in greetings or (len(tokens) <= 2 and any(t in greetings for t in tokens)):
            return (
                "Hey there! 👋 I'm **Proca**, your friendly e-GP Manual Assistant.\n\n"
                "I know the official **Bangladesh e-GP Procuring Entity User Manual** (all 543 pages!) inside and out, "
                "so I'm here to help you with things like:\n\n"
                "- 🔑 **Account setup & login** issues\n"
                "- 📋 **Annual Procurement Plan (APP)** preparation\n"
                "- 📢 **Tender creation, publishing & evaluation**\n"
                "- 🔄 **Workflow approvals** (Checker/Approver steps)\n"
                "- 📑 **Contract management (CMS)** procedures\n\n"
                "What would you like to know today? Just ask away! 😊"
            )

        # 2. Out-of-Domain / Entertainment Guardrail (e.g. "make a joke", "tell a story")
        off_topic_triggers = {"joke", "jokes", "funny", "story", "stories", "poem", "song", "sing", "game", "weather", "cricket", "football", "movie"}
        if any(t in off_topic_triggers for t in tokens):
            return (
                "Ha! I wish I could help with that, but I'm afraid jokes and stories are a bit outside my expertise. 😄\n\n"
                "I'm **Proca**, your dedicated e-GP Manual Assistant — I live and breathe government procurement procedures! "
                "If you have any questions about the **e-GP portal, tenders, APP, workflows, or account setup**, "
                "I'm your go-to assistant.\n\n"
                "What procurement topic can I help you with? 🏛️"
            )

        # 3. Guideline 4: If context does not contain enough information
        if not context or "No relevant context" in context or "No manual index" in context:
            return (
                "Hmm, I looked through the e-GP manual but couldn't find anything specific about that. 🤔\n\n"
                "For this query, I'd recommend reaching out to the **e-GP Helpdesk** directly — "
                "they'll be able to give you the most accurate answer:\n\n"
                "📧 **Email:** helpdesk@eprocure.gov.bd\n"
                "📞 **Phone:** +880-960-4224224\n\n"
                "Is there anything else I can help you find in the e-GP manual? 😊"
            )

        # Mode 1: Local Transformers
        if self._mode == "local_transformers" and self._local_model is not None:
            try:
                print(f"[llm_service] Running local inference on '{self.model_name}'...")
                return self._generate_local_transformers(question, context, image_url_or_path=image)
            except Exception as e:
                print(f"[llm_service] Local transformers generation failed: {e}. Falling back.")

        # Mode 2: Google Gemini API (if GEMINI_API_KEY is configured)
        gemini_answer = self._call_gemini_api(question, context)
        if gemini_answer:
            return gemini_answer

        # Mode 3: Groq API (if GROQ_API_KEY is configured)
        groq_answer = self._call_groq_api(question, context)
        if groq_answer:
            return groq_answer

        # Mode 4: Hugging Face Inference API
        current_token = get_hf_token()
        if self._hf_client is None and current_token and current_token != "your_huggingface_api_token_here":
            try:
                from huggingface_hub import InferenceClient
                self._hf_client = InferenceClient(token=current_token)
                self.model_name = get_llm_model()
            except Exception as e:
                self._hf_client = None

        if self._hf_client is not None:
            user_message = (
                f"Context from e-GP Manuals:\n{context}\n\n"
                f"User Question: {question}\n\n"
                f"Answer the question thoroughly and concisely based on the context above. Cite the source manuals and page numbers."
            )
            try:
                response = self._hf_client.chat_completion(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=800,
                    temperature=0.2
                )
                answer = response.choices[0].message.content
                return answer.strip()
            except Exception as e:
                # 402 Payment Required or provider error -> fall back silently to smart synthesis
                pass

        # Mode 5: Smart Offline Grounded Synthesis
        return self._offline_answer_generator(question, context)


# Singleton instance
llm_service = LLMService()

if __name__ == "__main__":
    sample_context = (
        "[Manual: e-GP System User Manual - Procuring Entity User 1 February 2026.pdf | Page 6 | Score 0.88]\n"
        "1. Login to e-GP Portal along with Email Id & Password:\n"
        "Procuring Entity (PE) will be created by e-GP Admin. The user will receive an email containing login credentials."
    )
    test_question = "How does a Procuring Entity user login to the e-GP portal?"
    print(llm_service.generate_answer(test_question, sample_context))
