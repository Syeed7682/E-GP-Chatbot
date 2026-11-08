"""
Test Chat API (backend/tests/test_chat.py).
Tests chat endpoint responses and grounding.
"""
import sys
from pathlib import Path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.services.llm_service import _image_data_url, _user_message_content
from app.services.llm_service import is_vague_steps_request
from app.services import retrieval_service as retrieval_service_module
from app.services import vision_service as vision_service_module
from app.services.llm_service import llm_service

client = TestClient(app)

def test_qwen_vision_payload_includes_image_data_url():
    image = "aGVsbG8="
    content = _user_message_content("Analyze this screenshot", image, "image/jpeg")

    assert content == [
        {"type": "text", "text": "Analyze this screenshot"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,aGVsbG8="}},
    ]
    assert _image_data_url("data:image/webp;base64,abc", "image/png") == "data:image/webp;base64,abc"

def test_screenshot_uses_qwen_by_default(monkeypatch):
    captured = {}
    monkeypatch.setattr(vision_service_module.vision_service, "extract_text_from_base64", lambda _: "")
    monkeypatch.setattr(retrieval_service_module.retrieval_service, "retrieve", lambda *args, **kwargs: ("manual context", []))

    def fake_generate_answer(question, context, **kwargs):
        captured.update(kwargs)
        return "Grounded answer"

    monkeypatch.setattr(llm_service, "generate_answer", fake_generate_answer)
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
    assert "Qwen/Qwen2.5-VL-3B-Instruct" in response.json()["model_used"]

def test_chat_health():
    res = client.get("/api/chat/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("healthy", "index_not_loaded")
    print("[PASS] Chat health check")

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
        return "APP steps"

    monkeypatch.setattr(retrieval_service_module.retrieval_service, "retrieve", fake_retrieve)
    monkeypatch.setattr(llm_service, "generate_answer", fake_generate_answer)

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
    monkeypatch.setattr(llm_service, "generate_answer", lambda *args, **kwargs: "  ")

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
