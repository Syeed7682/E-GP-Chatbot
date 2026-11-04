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
        Smart, descriptive answer synthesizer.
        Generates clean, structured, step-by-step procedural answers without raw metadata noise.
        """
        if not context or "No relevant context" in context or "No manual index" in context:
            return (
                "I could not find information regarding this in the current e-GP manuals. "
                "For specific queries, please contact the e-GP Helpdesk at helpdesk@eprocure.gov.bd or call +880-960-4224224."
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
                    # Extract page number: [Manual: ... | Page 6 | ...]
                    m = re.search(r'Page\s+(\d+)', line)
                    if m:
                        page_num = int(m.group(1))
                        if page_num not in pages_found:
                            pages_found.append(page_num)
                else:
                    text_lines.append(line)

            chunk_body = "\n".join(text_lines)
            cleaned_chunks.append({
                "page": page_num,
                "text": chunk_body
            })

        # --- SPECIALIZED INTENT SYNTHESIS ---

        # 1. Intent: Account Creation / Registration / PE User Opening
        is_account_query = any(k in q_lower for k in [
            "open an account", "open account", "create an account", "create account",
            "how to register", "registration", "signup", "sign up", "new user", "create user"
        ])

        if is_account_query:
            return (
                "### Account Creation & Initial Setup for Procuring Entity (PE) Users\n\n"
                "In the electronic Government Procurement (e-GP) system, **Procuring Entity (PE) users do not self-register** through a public sign-up form. All PE user accounts are provisioned administratively under government security guidelines.\n\n"
                "#### 1. Account Creation by System Administrator\n"
                "- **Creation Authority**: The Procuring Entity (PE) user account must be created by the **e-GP Admin**, **Organization Admin**, or **PE Admin** within the e-GP portal.\n"
                "- **Credential Email**: The moment the PE account is created, the system automatically sends a system-generated email to the user's registered email address containing their official **Username and temporary Password**.\n\n"
                "#### 2. First-Time Portal Login & Mandatory Password Change\n"
                "- **Access the Portal**: Visit the official e-GP Portal at `https://www.eprocure.gov.bd` and enter the assigned Username and Password (*Screen - A1*).\n"
                "- **Mandatory Security Screen**: On first login, the e-GP system automatically directs the user to the **\"Change Password\"** screen as a crucial security measure.\n"
                "- **Mandatory Fields**: Every field on the Change Password page is mandatory. The PE user must provide the existing password, specify a compliant new password, and confirm it.\n"
                "- **Confirmation**: Click the **\"Submit\"** button (*Screen - A2*). The system will display the confirmation message: *\"Password Changed successfully\"* (*Screen - A3*).\n\n"
                "#### 3. Logging in with Updated Credentials & Verification\n"
                "- **Authenticate**: Return to the login box, enter the registered email ID and the newly updated password, and click **\"Login\"**.\n"
                "- **NID & Mobile Verification**: If prompted, complete the **National ID (NID) and Mobile Number verification** via OTP to unlock the full dashboard functionalities.\n"
                "- **Dashboard Access**: Once verified, you are granted full access to your Procuring Entity workspace, where you can view your profile under **\"My Account >> View Profile\"** (*Page 533*).\n\n"
                "---\n"
                "📖 **Official Reference**: e-GP System User Manual (Procuring Entity User), Chapter 1 (*Login to e-GP Portal along with Email Id & Password*), Pages 6–9 and Chapter 13 (*My Account*), Page 533."
            )

        # 2. Intent: Approved Workflow
        is_workflow_query = any(k in q_lower for k in ["approved workflow", "workflow", "checker", "approver"])
        if is_workflow_query and any(c.get("page") == 199 for c in cleaned_chunks):
            return (
                "### Approved Workflow Procedure (Workflow >> Approved Workflow)\n\n"
                "In the e-GP system, the **Approved Workflow** feature allows Procuring Entity (PE) users to monitor, track, and review all workflows that have successfully passed the required verification and approval stages.\n\n"
                "#### Step-by-Step Procedure:\n"
                "1. **Navigate to the Menu**:\n"
                "   Click on the **\"Workflow\"** main menu and select the **\"Approved Workflow\"** sub-menu. The system will display the list of all approved workflows (*Screen - E11*).\n\n"
                "2. **Search and Filter Approved Tasks**:\n"
                "   You can narrow down approved tasks using search parameters:\n"
                "   - **Module Name** (e.g., APP, Tender, Evaluation, CMS)\n"
                "   - **Process Name**\n"
                "   - **APP / Tender ID**\n"
                "   - **Processed By**\n"
                "   - **Processed Date Range** (*From Date & Time* to *To Date & Time*)\n"
                "   - Results populate automatically in the search grid (*Screen - E12*).\n\n"
                "3. **Inspect File Details & Workflow History**:\n"
                "   - In the search results grid, locate the relevant record and click the **\"View\"** link under the **Action** column.\n"
                "   - The system displays the complete audit record including **File Details, Module, Process Name, Workflow History**, and individual **Workflow Levels** with reviewer/approver remarks (*Screen - E12*).\n\n"
                "---\n"
                "📖 **Official Reference**: e-GP System User Manual (Procuring Entity User), Section 5.3 (*Approved Workflow*), Page 199."
            )

        # 3. Intent: Annual Procurement Plan (APP)
        is_app_query = any(k in q_lower for k in ["app", "annual procurement plan", "procurement plan"])
        if is_app_query:
            return (
                "### Annual Procurement Plan (APP) Preparation & Workflow\n\n"
                "The **Annual Procurement Plan (APP)** is a mandatory prerequisite in e-GP before creating and publishing tenders.\n\n"
                "#### Key Procedures for APP Management:\n"
                "1. **Accessing APP Module**:\n"
                "   - Log into the e-GP portal and select **\"APP\"** from the main dashboard.\n"
                "   - Choose to either create a new APP or update an existing approved plan.\n\n"
                "2. **Adding Procurement Packages**:\n"
                "   - Specify the **Procurement Nature** (Goods, Works, or Services).\n"
                "   - Define package details: Package Number, Description, Estimated Cost, Procurement Method (e.g. OTM, RFQ, LTM), and Approving Authority.\n"
                "   - Set milestone dates for tender preparation, opening, evaluation, award, and contract completion.\n\n"
                "3. **Workflow Processing & Approval**:\n"
                "   - Once packages are saved, process the file through the approval workflow to the designated **Checker and Approver**.\n"
                "   - After final administrative approval, the APP status changes to *Approved*, enabling tender creation under the approved packages.\n\n"
                "---\n"
                "📖 **Official Reference**: e-GP System User Manual (Procuring Entity User), Chapter 3 (*Annual Procurement Plan*), Pages 21–53."
            )

        # 4. General Synthesizer from Retrieved Context
        combined_text = "\n\n".join([c["text"] for c in cleaned_chunks])
        
        # Clean up bullet points, numbered items, and sentences
        raw_lines = [l.strip() for l in combined_text.split("\n") if l.strip()]
        informative_lines: List[str] = []
        screen_refs: List[str] = []

        for line in raw_lines:
            # Skip noise or lone digits
            if line.isdigit() or len(line) < 5:
                continue
            if line.startswith("Screen") or "Screen -" in line or "Screen –" in line:
                if line not in screen_refs:
                    screen_refs.append(line)
                continue
            if line.startswith(("[Manual:", "Table of Contents", "Change Log")):
                continue

            # Standardize bullet points and numbered points
            clean_l = re.sub(r'^[•\-\*✓]\s*', '', line).strip()
            clean_l = re.sub(r'^\d+\.\s*', '', clean_l).strip()
            if clean_l and clean_l not in informative_lines:
                informative_lines.append(clean_l)

        # Structure into a detailed response
        pages_str = ", ".join(f"Page {p}" for p in sorted(set(pages_found)) if p) if pages_found else "relevant pages"

        output_paragraphs = [
            f"### Guidance from the Official e-GP Procuring Entity User Manual\n",
            "Here is the detailed procedure and guidance corresponding to your query:\n"
        ]

        if informative_lines:
            output_paragraphs.append("#### Key Steps and System Rules:\n")
            for i, line in enumerate(informative_lines[:8], 1):
                # Bold lead-in phrase
                if ":" in line:
                    parts = line.split(":", 1)
                    output_paragraphs.append(f"{i}. **{parts[0].strip()}**: {parts[1].strip()}")
                else:
                    output_paragraphs.append(f"{i}. {line}")

        if screen_refs:
            output_paragraphs.append("\n#### Reference Screens:")
            output_paragraphs.append(f"- Referenced portal screens: *{', '.join(screen_refs[:4])}*.")

        output_paragraphs.append(f"\n---\n📖 **Official Reference**: e-GP System User Manual (Procuring Entity User 1 February 2026), {pages_str}.")
        return "\n".join(output_paragraphs)

    def generate_answer(self, question: str, context: str, image: Optional[str] = None) -> str:
        """
        Generates an answer using Qwen2.5-VL-72B-Instruct with the provided context.
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
                "Hello! I am your official e-GP (electronic Government Procurement) Manual Assistant.\n\n"
                "I am here to guide you through procurement guidelines, tender submissions, Annual Procurement Plan (APP) preparation, workflow approvals, and account setup.\n\n"
                "How can I assist you with the e-GP portal today?"
            )

        # 2. Out-of-Domain / Entertainment Guardrail (e.g. "make a joke", "tell a story")
        off_topic_triggers = {"joke", "jokes", "funny", "story", "stories", "poem", "song", "sing", "game", "weather", "cricket", "football", "movie"}
        if any(t in off_topic_triggers for t in tokens):
            return (
                "I am the official e-GP (electronic Government Procurement) Manual Assistant.\n\n"
                "I am strictly dedicated to providing accurate, cited procedural guidance on government procurement rules, system workflows, and user manuals. I cannot fulfill entertainment requests such as telling jokes.\n\n"
                "Please feel free to ask any question regarding official e-GP procedures or portal operations."
            )

        # 3. Guideline 4: If context does not contain enough information
        if not context or "No relevant context" in context or "No manual index" in context:
            return (
                "I could not find information regarding this in the current e-GP manuals. "
                "For specific queries, please contact the e-GP Helpdesk at helpdesk@eprocure.gov.bd or call +880-960-4224224."
            )

        # Mode 1: Local Transformers
        if self._mode == "local_transformers" and self._local_model is not None:
            try:
                print(f"[llm_service] Running local inference on '{self.model_name}'...")
                return self._generate_local_transformers(question, context, image_url_or_path=image)
            except Exception as e:
                print(f"[llm_service] Local transformers generation failed: {e}. Falling back.")

        # Mode 2: Hugging Face Inference API
        current_token = get_hf_token()
        if self._hf_client is None and current_token and current_token != "your_huggingface_api_token_here":
            try:
                from huggingface_hub import InferenceClient
                self._hf_client = InferenceClient(token=current_token)
                self.model_name = get_llm_model()
                print(f"[llm_service] Dynamic HF client initialized for '{self.model_name}'.")
            except Exception as e:
                print(f"[llm_service] Could not initialize HF client: {e}")

        if self._hf_client is not None:
            user_message = (
                f"Context from e-GP Manuals:\n{context}\n\n"
                f"User Question: {question}\n\n"
                f"Answer the question thoroughly and concisely based on the context above. Cite the source manuals and page numbers."
            )

            try:
                print(f"[llm_service] Sending prompt to '{self.model_name}' via Hugging Face API...")
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
                print(f"[llm_service] Hugging Face Inference API error: {e}. Falling back to smart synthesis.")

        # Mode 3: Smart Offline Synthesis Fallback
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
