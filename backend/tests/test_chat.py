"""
Test Chat API (backend/tests/test_chat.py).
Tests chat endpoint responses and grounding.
"""
import sys
from pathlib import Path
import pytest
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.services.llm_service import (
    GROQ_TEXT_MODEL,
    GROQ_VISION_MODEL,
    LLMService,
    _image_data_url,
    _user_message_content,
    load_system_prompt,
)
from app.services.llm_service import is_vague_steps_request
from app.services import retrieval_service as retrieval_service_module
from app.services import vision_service as vision_service_module
from app.services.llm_service import llm_service
from app.services.qa_service import qa_service

client = TestClient(app)

def test_qwen_vision_payload_includes_image_data_url():
    image = "aGVsbG8="
    content = _user_message_content("Analyze this screenshot", image, "image/jpeg")

    assert content == [
        {"type": "text", "text": "Analyze this screenshot"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,aGVsbG8="}},
    ]
    assert _image_data_url("data:image/webp;base64,abc", "image/png") == "data:image/webp;base64,abc"

def test_screenshot_uses_vision_model_by_default(monkeypatch):
    captured = {}
    monkeypatch.setattr(vision_service_module.vision_service, "extract_text_from_base64", lambda _: "")
    monkeypatch.setattr(retrieval_service_module.retrieval_service, "retrieve", lambda *args, **kwargs: ("manual context", []))

    def fake_generate_answer(question, context, **kwargs):
        captured.update(kwargs)
        return "Grounded answer", "test/vision-model", False

    monkeypatch.setattr(llm_service, "generate_answer_with_metadata", fake_generate_answer)
    response = client.post(
        "/api/chat",
        json={
            "question": "What is shown?",
            "image_base64": "data:image/jpeg;base64,aGVsbG8=",
            "image_mime": "image/jpeg",
        },
    )

    assert response.status_code == 200
    assert captured["use_alt_model"] is False
    assert captured["image_mime"] == "image/jpeg"
    assert "test/vision-model" in response.json()["model_used"]

def test_direct_q_and_a_match_returns_source_answer_verbatim(monkeypatch):
    exact_answer = "Open My Account, select Verify NID, and follow the displayed instructions."
    qa_source = {
        "source": "e-GP System Q&A.txt",
        "source_type": "qa",
        "page": None,
        "chunk_id": None,
        "question_number": 1,
        "module": "Portal Access",
        "score": 1.0,
        "snippet": exact_answer,
        "answer": exact_answer,
        "direct_match": True,
        "image_path": None,
    }
    monkeypatch.setattr(
        retrieval_service_module.retrieval_service,
        "retrieve",
        lambda *args, **kwargs: ("Q&A context", [qa_source]),
    )
    monkeypatch.setattr(
        llm_service,
        "generate_answer_with_metadata",
        lambda *args, **kwargs: pytest.fail("A direct Q&A answer should not be rewritten by an LLM"),
    )

    response = client.post(
        "/api/chat",
        json={"question": "How do I verify my NID in e-GP?"},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["answer"] == exact_answer
    assert result["sources"][0]["source_type"] == "qa"
    assert result["sources"][0]["page"] is None
    assert result["sources"][0]["question_number"] == 1
    assert result["model_used"] == "e-GP System Q&A.txt (verbatim)"

def test_chat_returns_matching_file_answer_verbatim(monkeypatch):
    question = "How to Verify National ID (NID) for PE and Vendor User Accounts?"
    expected_answer = qa_service.search(question, limit=1)[0]["record"]["answer"]
    monkeypatch.setattr(
        llm_service,
        "generate_answer_with_metadata",
        lambda *args, **kwargs: pytest.fail("A matching Q&A entry should not be rewritten"),
    )

    response = client.post("/api/chat", json={"question": question})

    assert response.status_code == 200
    result = response.json()
    assert result["answer"] == expected_answer
    assert result["sources"][0]["source"] == "e-GP System Q&A.txt"
    assert result["sources"][0]["question_number"] == 1

def test_related_q_and_a_entry_is_sent_to_the_answer_model(monkeypatch):
    captured = {}
    answer_text = "Follow the Q&A instructions and verify the submitted details."
    qa_source = {
        "source": "e-GP System Q&A.txt",
        "source_type": "qa",
        "page": None,
        "chunk_id": None,
        "question_number": 2,
        "module": "Portal Access",
        "score": 0.62,
        "snippet": answer_text,
        "answer": answer_text,
        "direct_match": False,
        "image_path": None,
    }
    context = (
        "[Supplemental Q&A: e-GP System Q&A.txt | Module: Portal Access | Question 2]\n"
        "Q: How do I verify a mobile number?\nA:\n" + answer_text
    )
    monkeypatch.setattr(
        retrieval_service_module.retrieval_service,
        "retrieve",
        lambda *args, **kwargs: (context, [qa_source]),
    )

    def fake_generate(question, retrieved_context, **kwargs):
        captured["context"] = retrieved_context
        return "Generated answer from the retrieved Q&A.", "test/model", False

    monkeypatch.setattr(llm_service, "generate_answer_with_metadata", fake_generate)

    response = client.post(
        "/api/chat",
        json={"question": "Can you explain mobile verification?"},
    )

    assert response.status_code == 200
    assert captured["context"] == context
    assert "e-GP System Q&A.txt" in captured["context"]
    assert answer_text in captured["context"]
    assert response.json()["answer"] == "Generated answer from the retrieved Q&A."

def test_chat_replaces_retrieval_context_echo_with_the_q_and_a_answer(monkeypatch):
    answer_text = "Navigate to e-CMS, open Physical Progress, and generate the invoice."
    qa_source = {
        "source": "e-GP System Q&A.txt",
        "source_type": "qa",
        "page": None,
        "chunk_id": None,
        "question_number": 801,
        "module": "e-CMS Physical Progress",
        "score": 0.26,
        "snippet": answer_text,
        "answer": answer_text,
        "direct_match": False,
        "image_path": None,
    }
    monkeypatch.setattr(
        retrieval_service_module.retrieval_service,
        "retrieve",
        lambda *args, **kwargs: ("[Supplemental Q&A: e-GP System Q&A.txt | Relevance: 0.26]\nQ: ...\nA:\n" + answer_text, [qa_source]),
    )
    monkeypatch.setattr(
        llm_service,
        "generate_answer_with_metadata",
        lambda *args, **kwargs: (
            "Supplemental Q&A: e-GP System Q&A.txt | Module: e-CMS Physical Progress\n"
            "Q: How do I process the payment?\nA: " + answer_text,
            "test/model",
            False,
        ),
    )

    response = client.post(
        "/api/chat",
        json={"question": "Paypoint Acceptance and Payment Disbursement?"},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["answer"] == answer_text
    assert "Relevance:" not in result["answer"]
    assert result["sources"][0]["question_number"] == 801
    assert result["model_used"] == "e-GP System Q&A.txt (verbatim)"

def test_chat_synthesizes_manual_answer_when_model_echoes_mixed_retrieval_context(monkeypatch):
    manual_context = (
        "[Manual: official manual | Page 388 | Relevance: 1.00]\n"
        "In this stage, the iBAS++ bill status in e-GP system will be changed as "
        "Paypoint Accept DDO Bill."
    )
    qa_context = (
        "[Supplemental Q&A: e-GP System Q&A.txt | Module: DDO Integration | Question 881]\n"
        "Q: How do DDOs submit e-GP bills?\nA:\nFollow a different transfer procedure."
    )
    sources = [
        {
            "source": "e-GP System Q&A.txt",
            "source_type": "qa",
            "page": None,
            "chunk_id": None,
            "question_number": 881,
            "module": "DDO Integration",
            "score": 0.38,
            "snippet": "Follow a different transfer procedure.",
            "answer": "Follow a different transfer procedure.",
            "direct_match": False,
            "image_path": None,
        },
        {
            "source": "official manual",
            "source_type": "manual",
            "page": 388,
            "chunk_id": 1,
            "score": 1.0,
            "snippet": "Paypoint Accept DDO Bill",
            "image_path": None,
        },
    ]
    captured = {}
    monkeypatch.setattr(
        retrieval_service_module.retrieval_service,
        "retrieve",
        lambda *args, **kwargs: (qa_context + "\n\n---\n\n" + manual_context, sources),
    )
    monkeypatch.setattr(
        llm_service,
        "generate_answer_with_metadata",
        lambda *args, **kwargs: (
            "The bill status changes to Paypoint Accept DDO Bill. "
            "[Supplemental Q&A: e-GP System Q&A.txt | Relevance: 0.38] "
            "Q: How do DDOs submit bills? A: Follow another procedure.",
            "test/model",
            False,
        ),
    )

    def offline_answer(question, context):
        captured["context"] = context
        return "After the bill is accepted, its e-GP status becomes **Paypoint Accept DDO Bill**."

    monkeypatch.setattr(llm_service, "_offline_answer_generator", offline_answer)

    response = client.post(
        "/api/chat",
        json={"question": "what Paypoint Accept DDO Bill"},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == (
        "After the bill is accepted, its e-GP status becomes **Paypoint Accept DDO Bill**."
    )
    assert captured["context"] == manual_context

def test_chat_health():
    res = client.get("/api/chat/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("healthy", "index_not_loaded")
    print("[PASS] Chat health check")

def test_chat_question_suggestions_include_all_q_and_a_questions():
    response = client.get("/api/chat/questions")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1000
    assert len(data["questions"]) == 1000
    assert data["questions"][0]["question_number"] == 1
    assert data["questions"][0]["question"]
    assert data["questions"][0]["module"]

def test_chat_debarment():
    res = client.post("/api/chat", json={"question": "what is debarment?", "top_k": 3})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "debar" in data["answer"].lower() or "suspension" in data["answer"].lower()
    assert len(data["sources"]) > 0
    print("[PASS] Chat debarment test passed")

def test_chat_delete_tender():
    res = client.post("/api/chat", json={"question": "How to delete a tender?", "top_k": 3})
    assert res.status_code == 200
    data = res.json()
    assert "cancel" in data["answer"].lower() or "delete" in data["answer"].lower()
    print("[PASS] Chat delete tender test passed")


def test_offline_answer_uses_concise_prose_without_citations_or_boilerplate():
    context = (
        "[Manual: e-GP System User Manual | Page 7 | Score 0.9]\n"
        "1.6 After the password change is successful, the Procuring Entity user must log in.\n"
        "Screen-A3 1.7 Enter the registered email ID and newly set password in the login fields.\n"
        "As shown in Screen-A3."
    )

    answer = llm_service._offline_answer_generator(
        "What should I do after changing my password?",
        context,
    )

    assert "must log in" in answer.lower()
    assert "registered email" in answer.lower()
    assert "page 7" not in answer.lower()
    assert "screen-a3" not in answer.lower()
    assert "key details" not in answer.lower()
    assert "would you like" not in answer.lower()
    assert not answer.lstrip().startswith(("1.", "**1."))

def test_offline_answer_synthesizes_the_paypoint_bill_status_from_manual_context():
    context = (
        "[Manual: official manual | Page 388]\n"
        "To accept the bill, click on Accept button.\n"
        "Then a pop-up is displayed with notification message that bill is accepted.\n"
        "In this stage, the iBAS++ bill status in e-GP system will be changed as "
        "\uFFFDPaypoint Accept DDO Bill\uFFFD."
    )

    answer = llm_service._offline_answer_generator(
        "what Paypoint Accept DDO Bill",
        context,
    )

    assert answer == (
        "The manual identifies **Paypoint Accept DDO Bill** as the e-GP bill status shown after "
        "the bill is accepted. It says to click **Accept**; after the confirmation appears, "
        "the status changes to this label."
    )

def test_offline_tender_fee_answer_uses_structured_sections_and_preserves_source_values():
    context = (
        "[Manual: Official e-GP Manual | Page 60]\n"
        "4.1.14 Based on the Package Estimated Cost for Procurement Type of NCT, "
        "Tender/Proposal Document Price (In BDT) will be added automatically.\n"
        "Estimated Cost (Taka) Current Fee (Taka) Revised Fee (Taka)\n"
        "Up to 10,000,00 1,000.00 500.00\n"
        "Up to 25,000,00 1,000.00 1,000.00\n"
        "Up to 50,000,00 1,000.00 1,500.00\n"
        "Up to 2,00,000,00 2,000.00 2,500.00\n"
        "Up to 10,00,000,00 4,000.00 4,000.00\n"
        "Up to 30,00,000,00 4,000.00 5,000.00\n"
        "Up to 50,00,000,00 4,000.00 6,000.00\n"
        "Up to 100,00,000,00 4,000.00 7,000.00\n"
        "Above 100,00,000,00 4,000.00 10,000.00\n"
        "Tender Document Fee for International Competitive Tender (ICT) will be BDT. 12,000.00.\n"
    )

    answer = llm_service._offline_answer_generator("Explain this price schedule.", context)

    assert "### 1. National Competitive Tendering (NCT)" in answer
    assert "| Estimated package cost (BDT) | Current fee (BDT) | Revised fee (BDT) |" in answer
    assert "| Up to 10,000,00 | 1,000.00 | 500.00 |" in answer
    assert "| Up to 2,00,000,00 | 2,000.00 | 2,500.00 |" in answer
    assert "| Up to 30,00,000,00 | 4,000.00 | 5,000.00 |" in answer
    assert "| Above 100,00,000,00 | 4,000.00 | 10,000.00 |" in answer
    assert "### 2. International Competitive Tendering (ICT)" in answer
    assert "BDT 12,000.00" in answer
    assert "### Summary" in answer
    assert "**Source:** Section 4.1.14" in answer
    assert "Not specified" not in answer
    assert "Pre-Tender" not in answer

def test_generic_manual_question_gets_a_grounded_answer():
    context = (
        "[Manual: e-GP System User Manual | Page 6 | Relevance: 0.9]\n"
        "For users logging in for the first time, the system guides the PE to a Change Password screen. "
        "This is a crucial step aimed at enhancing the overall security of the e-GP Portal."
    )

    answer = llm_service._offline_answer_generator(
        "What does the manual say about crucial?",
        context,
    )

    assert answer == (
        "This is a crucial step aimed at enhancing the overall security of the e-GP Portal."
    )

def test_app_answer_uses_professional_tone():
    answer = llm_service._offline_answer_generator(
        "How do I prepare an Annual Procurement Plan?",
        "Annual Procurement Plan APP procurement package approval workflow",
    )

    assert "Absolutely!" not in answer
    assert "Let me walk you through" not in answer
    assert "Would you like" not in answer
    assert not any(symbol in answer for symbol in ("😊", "📋", "✅", "💰"))
    assert "Checker" in answer and "Approver" in answer
    assert answer.startswith("Create the Annual Procurement Plan")

def test_vague_steps_request_asks_which_process():
    assert is_vague_steps_request("tell me the steps")
    assert is_vague_steps_request("what is the next process?")
    assert not is_vague_steps_request("tell me the APP steps")

    answer = llm_service.generate_answer("tell me the steps", "No relevant context found in manuals.")

    assert answer == (
        "Which e-GP process would you like the steps for? For example, creating or submitting an APP, "
        "creating a tender, or evaluating bids."
    )
    assert "Helpdesk" not in answer

def test_chat_uses_previous_topic_for_steps_followup(monkeypatch):
    captured = {}

    def fake_retrieve(query, **kwargs):
        captured["retrieval_query"] = query
        return "APP creation and approval details", []

    def fake_generate_answer(question, context, **kwargs):
        captured["answer_question"] = question
        return "APP steps", "test/model", False

    monkeypatch.setattr(retrieval_service_module.retrieval_service, "retrieve", fake_retrieve)
    monkeypatch.setattr(llm_service, "generate_answer_with_metadata", fake_generate_answer)

    response = client.post(
        "/api/chat",
        json={"question": "tell me the steps", "previous_question": "How do I prepare an APP?"},
    )

    assert response.status_code == 200
    assert "APP" in captured["retrieval_query"]
    assert "numbered steps" in captured["retrieval_query"]
    assert "APP" in captured["answer_question"]
    assert "numbered steps" in captured["answer_question"]
    assert response.json()["answer"] == "APP steps"

def test_chat_clarifies_vague_steps_without_retrieval(monkeypatch):
    def unexpected_retrieval(*args, **kwargs):
        raise AssertionError("Vague steps request should not trigger manual retrieval")

    monkeypatch.setattr(retrieval_service_module.retrieval_service, "retrieve", unexpected_retrieval)

    response = client.post("/api/chat", json={"question": "tell me the steps"})

    assert response.status_code == 200
    assert "Which e-GP process" in response.json()["answer"]
    assert response.json()["sources"] == []

def test_steps_followup_never_returns_an_empty_answer(monkeypatch):
    monkeypatch.setattr(
        retrieval_service_module.retrieval_service,
        "retrieve",
        lambda *args, **kwargs: (
            "[Manual: Official e-GP Manual | Page 7]\n"
            "1.7 The user should enter their registered email ID and newly set password.\n"
            "1.8 Click the Login button to access the portal.",
            [],
        ),
    )
    monkeypatch.setattr(
        llm_service,
        "generate_answer_with_metadata",
        lambda *args, **kwargs: ("  ", "test/model", False),
    )

    response = client.post(
        "/api/chat",
        json={
            "question": "tell me the steps",
            "previous_question": "How do I log in and change my password?",
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"].strip()
    assert "registered email" in response.json()["answer"]

def test_step_answer_is_synthesized_from_full_manual_context():
    context, _ = retrieval_service_module.retrieval_service.retrieve(
        "Provide concise numbered steps for: How do I log in and change my password?",
        top_k=3,
        include_page_context=True,
    )

    answer = llm_service.generate_answer(
        "Provide concise numbered steps for: How do I log in and change my password?",
        context,
    )

    assert answer.startswith("1. ")
    assert "Change Password" in answer
    assert "Submit" in answer
    assert "registered email ID" in answer
    assert "newly set password" in answer
    assert "Login" in answer
    assert "helpdesk" not in answer.lower()
    assert "As shown in" not in answer

def test_steps_followup_chat_returns_login_procedure():
    response = client.post(
        "/api/chat",
        json={
            "question": "what are the steps.",
            "previous_question": "How do I log in and change my password?",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    answer = response.json()["answer"]
    assert answer.startswith("1. ")
    assert "Change Password" in answer
    assert "Submit" in answer
    assert "registered email ID" in answer
    assert "newly set password" in answer
    assert "Login" in answer
    assert len(response.json()["sources"]) > 0


if __name__ == "__main__":
    test_chat_health()
    test_chat_debarment()
    test_chat_delete_tender()
    print("All chat API tests PASSED!")
def test_model_prompt_enforces_manual_grounding_and_structured_answer_format():
    import requests
    captured = {}

    class SuccessfulResponse:
        status_code = 200

        def json(self):
            return {"choices": [{"message": {"content": "The manual supports this conclusion."}}]}

    def fake_post(url, headers, json, timeout):
        captured["payload"] = json
        captured["authorization"] = headers["Authorization"]
        return SuccessfulResponse()

    import app.services.llm_service as llm_service_module
    from unittest.mock import patch
    with patch.object(llm_service_module, "get_groq_api_key", return_value="test-key"), patch.object(requests, "post", fake_post):
        service = LLMService.__new__(LLMService)
        service.system_prompt = load_system_prompt()
        answer = service._call_groq_api(
            "What matters most during first login?",
            "For first-time users, change the initial password to enhance portal security.",
        )

    messages = captured["payload"]["messages"]

    assert answer == "The manual supports this conclusion."
    assert captured["authorization"] == "Bearer test-key"
    assert "answer using only the supplied official manual passages" in messages[0]["content"].lower()
    assert "markdown tables for fees" in messages[0]["content"].lower()
    assert "finish with a short **summary**" in messages[0]["content"].lower()
    assert "source** line with relevant manual section number(s)" in messages[0]["content"].lower()
    assert "preserve the source's exact number formatting" in messages[0]["content"].lower()
    assert "follow the system instructions" in messages[1]["content"].lower()
    assert "enhance portal security" in messages[1]["content"]
    assert captured["payload"]["model"] == GROQ_TEXT_MODEL


def test_groq_model_selection_and_multimodal_payload(monkeypatch):
    import requests
    import app.services.llm_service as llm_service_module
    from unittest.mock import patch
    captured = {}

    class SuccessfulResponse:
        status_code = 200

        def json(self):
            return {"choices": [{"message": {"content": "Grounded vision answer."}}]}

    def fake_post(url, headers, json, timeout):
        captured["payload"] = json
        return SuccessfulResponse()

    with patch.object(llm_service_module, "get_groq_api_key", return_value="test-key"), patch.object(requests, "post", fake_post):
        service = LLMService.__new__(LLMService)
        service.system_prompt = load_system_prompt()
        answer = service._call_groq_api(
            "What does this screen show?",
            "The manual describes the PE dashboard.",
            image="aGVsbG8=",
            image_mime="image/jpeg",
        )

    assert answer == "Grounded vision answer."
    assert captured["payload"]["model"] == GROQ_VISION_MODEL
    image_message = captured["payload"]["messages"][1]["content"]
    assert image_message[1]["image_url"]["url"] == "data:image/jpeg;base64,aGVsbG8="


def test_e1_image_and_e2_text_use_vision_model():
    service = LLMService.__new__(LLMService)
    service.system_prompt = load_system_prompt()
    service._mode = "offline_fallback"
    service._local_model = None
    captured = []
    service._call_groq_api = lambda *args, **kwargs: captured.append(kwargs["model"]) or "Grounded answer."
    service._call_gemini_api = lambda *args, **kwargs: None

    e1_image = service.generate_answer_with_metadata(
        "What is shown?", "Manual context", image="image-data"
    )
    e2_text = service.generate_answer_with_metadata(
        "Explain this workflow.", "Manual context", use_alt_model=True
    )
    e1_text = service.generate_answer_with_metadata(
        "What does the manual say?", "Manual context"
    )

    assert captured == [GROQ_VISION_MODEL, GROQ_VISION_MODEL, GROQ_TEXT_MODEL]
    assert e1_image[0] == "Grounded answer."
    assert e1_image[1:] == (GROQ_VISION_MODEL, False)
    assert e2_text[1:] == (GROQ_VISION_MODEL, False)
    assert e1_text[1:] == (GROQ_TEXT_MODEL, False)


def test_e2_groq_failure_uses_gemini_fallback_for_screenshots():
    service = LLMService.__new__(LLMService)
    service.system_prompt = load_system_prompt()
    service._mode = "offline_fallback"
    service._local_model = None
    captured = {}
    service._call_groq_api = lambda *args, **kwargs: None

    def gemini_fallback(question, context, image=None, image_mime="image/png"):
        captured.update(image=image, image_mime=image_mime)
        return "Grounded Gemini answer."

    service._call_gemini_api = gemini_fallback
    answer, model, was_offline = service.generate_answer_with_metadata(
        "What does this screen show?",
        "The manual describes the PE dashboard.",
        image="encoded-image",
        image_mime="image/jpeg",
        use_alt_model=True,
    )

    assert answer == "Grounded Gemini answer."
    assert model == "Gemini"
    assert not was_offline
    assert captured == {"image": "encoded-image", "image_mime": "image/jpeg"}


def test_gemini_screenshot_payload_keeps_the_image_mime_type(monkeypatch):
    import requests

    captured = {}

    class SuccessfulResponse:
        status_code = 200

        def json(self):
            return {
                "candidates": [
                    {"content": {"parts": [{"text": "Grounded answer."}]}}
                ]
            }

    def fake_post(url, headers, json, timeout):
        captured["payload"] = json
        return SuccessfulResponse()

    monkeypatch.setattr("app.services.llm_service.get_gemini_api_key", lambda: "test-key")
    monkeypatch.setattr(requests, "post", fake_post)

    service = LLMService.__new__(LLMService)
    service.system_prompt = load_system_prompt()

    answer = service._call_gemini_api(
        "What does this screen show?",
        "The manual describes the PE dashboard.",
        image="data:image/jpeg;base64,encoded",
    )

    assert answer == "Grounded answer."
    image_part = captured["payload"]["contents"][0]["parts"][0]["inline_data"]
    assert image_part == {"mime_type": "image/jpeg", "data": "encoded"}
