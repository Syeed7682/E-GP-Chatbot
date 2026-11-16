"""
Test Offline Functionality (backend/tests/test_offline.py).
Tests offline fallback generator and sync versioning.
"""
import sys
from pathlib import Path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.llm_service import llm_service
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_offline_synthesizer_debarment():
    context = (
        "If the HOPE intends to debar the suspended Tenderer, the HOPE must "
        "complete the debarment within 42 calendar days.\n"
        "After approving the debarment by HOPE, the debarment details will be "
        "displayed under the Debarred Tenderer List in e-GP Home Page."
    )
    answer = llm_service._offline_answer_generator("what is debarment?", context)

    assert answer.startswith("Debarment is a decision by the Head of Procuring Entity")
    assert "42 calendar days" in answer
    assert "Debarred Tenderer List" in answer
    assert "Step 1" not in answer
    assert "PPR-2008 Rule 127" not in answer


def test_offline_debarment_definition_does_not_invent_missing_evidence():
    answer = llm_service._offline_answer_generator(
        "what is debarment?",
        "Chapter 7 Debarment",
    )

    assert "couldn't find" in answer.lower()
    assert "helpdesk" in answer.lower()
    assert "16575" in answer


def test_offline_debarment_procedure_question_returns_procedure():
    answer = llm_service._offline_answer_generator(
        "How to ban a contractor?",
        (
            "7.1.1 To suspend any Tenderer PE needs to click on Debarment -> Suspension tab.\n"
            "7.1.2 To initiate the suspension process PE has to click on Initiate Suspension. "
            "Tenderer can be searched by e-Mail ID and Company Name.\n"
            "7.1.4 After suspension, the tenderer will not be able to participate in any tender or "
            "accept any NOA within 42 calendar days.\n"
            "7.1.5 The duration of the suspension period is 42 calendar days.\n"
            "7.1.8 The PE will upload the document. File now available in HOPE's hand to take the decision.\n"
            "If the HOPE intends to debar the suspended Tenderer, the HOPE must complete the debarment within "
            "42 calendar days. If the HOPE does not take any action within 42 calendar days, the suspension "
            "shall be automatically lifted.\n"
            "7.1.9 After approving the debarment by HOPE, the debarment details will be displayed under "
            "the Debarred Tenderer List."
        ),
    )

    assert "Debarment → Suspension" in answer
    assert "Initiate Suspension" in answer
    assert "42-calendar-day" in answer
    assert "automatically lifted" in answer
    assert "Debarred Tenderer List" in answer
    assert "3 years" not in answer
    assert "Cancel the tender" not in answer

def test_offline_synthesizer_delete_tender():
    ans = llm_service._offline_answer_generator("How to delete a tender?", "Chapter 4 Tender")
    assert "cancel" in ans.lower() or "cancellation" in ans.lower()
    assert "Page 178" in ans or "Page 191" in ans
    print("[PASS] Delete tender offline synthesizer test")

def test_sync_version_endpoint():
    res = client.get("/api/sync/version")
    assert res.status_code == 200
    data = res.json()
    assert "version" in data
    assert "hash" in data
    print("[PASS] Sync version endpoint test")

if __name__ == "__main__":
    test_offline_synthesizer_debarment()
    test_offline_synthesizer_delete_tender()
    test_sync_version_endpoint()
    print("All offline tests PASSED!")
