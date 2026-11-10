import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.services.qa_service import QAService, parse_qa_text
from app.services.retrieval_service import RetrievalService


def test_parser_preserves_answer_text_and_module():
    source = (
        "Module 1: Account Setup\n"
        "Question 1: Verify an account\n"
        "Q: How do I verify an account?\n"
        "Use the menu below:\n"
        "* Open  My Account  >  Verify.\n"
        "Question 2: Update an account\n"
        "Q: How do I update an account?\n"
        "Select Update.\n"
    )

    records = parse_qa_text(source)

    assert records == [
        {
            "question_number": 1,
            "module": "Account Setup",
            "title": "Verify an account",
            "question": "How do I verify an account?",
            "answer": "Use the menu below:\n* Open  My Account  >  Verify.",
        },
        {
            "question_number": 2,
            "module": "Account Setup",
            "title": "Update an account",
            "question": "How do I update an account?",
            "answer": "Select Update.",
        },
    ]


def test_parser_rejects_incomplete_qa_entries():
    with pytest.raises(ValueError, match="has no Q: line"):
        parse_qa_text("Module 1: Accounts\nQuestion 1: Verify an account\nNo answer")


def test_q_and_a_file_has_one_thousand_records_and_matches_verbatim():
    service = QAService()

    assert len(service.records) == 1000
    assert service.records[0]["source_files"] == [
        "e-GP System Q&A.txt",
        "e-GP System Q&A .docx",
    ]
    assert service._question_postings["national"]
    assert service._answer_postings["captcha"]
    assert len(service._question_vectors) == 1000
    assert service._question_vectors[0]
    result = service.search(
        "How to Verify National ID (NID) for PE and Vendor User Accounts?",
        limit=1,
    )

    assert len(result) == 1
    assert result[0]["record"]["question_number"] == 1
    assert result[0]["direct_match"] is True
    assert result[0]["record"]["question_number"] == 1
    assert result[0]["record"]["answer"].startswith(
        "To verify your National ID (NID) in the e-GP system, follow these step-by-step instructions:"
    )
    assert "* A green  \"NID Verified\"" in result[0]["record"]["answer"]


def test_q_and_a_search_does_not_match_unrelated_terms():
    service = QAService(settings.QA_DATA_PATH)

    assert service.search("weather forecast for tomorrow") == []


def test_q_and_a_search_matches_a_paraphrased_password_change_question():
    service = QAService()

    result = service.search("How to log in for the first time and change password?", limit=1)

    assert result
    assert result[0]["record"]["question_number"] == 3
    assert result[0]["direct_match"] is True


def test_q_and_a_search_can_retrieve_a_match_using_answer_terms():
    service = QAService()

    result = service.search("NID captcha attempts", limit=3)

    assert result
    assert result[0]["record"]["question_number"] == 1


def test_retrieval_returns_confident_q_and_a_without_loading_faiss():
    service = QAService()

    class EmptyFaiss:
        index = None
        metadata = []

        def load(self):
            return False

    retrieval = RetrievalService(
        emb_service=object(),
        f_service=EmptyFaiss(),
        q_service=service,
    )

    context, sources = retrieval.retrieve(
        "How to Verify National ID (NID) for PE and Vendor User Accounts?",
        top_k=3,
    )

    assert "Supplemental Q&A: e-GP System Q&A.txt, e-GP System Q&A .docx" in context
    assert "Question 1" in context
    assert sources[0]["direct_match"] is True
    assert sources[0]["question_number"] == 1
    assert sources[0]["page"] is None
