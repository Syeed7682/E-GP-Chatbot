"""
Q&A Chunker for Supplemental e-GP Q&A corpus.
Prepares normalized Q&A records with dedicated retrieval text, category, question, and answer.
"""
from typing import Any, Dict, List


def prepare_qa_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforms parsed Q&A records into retrieval-ready chunks.
    Separates question/retrieval_text from the full answer body.
    """
    output = []
    for item in records:
        question = item.get("question", "").strip()
        answer = item.get("answer", "").strip()
        category = item.get("category") or item.get("module") or "General Procurement"
        chunk_id = item.get("id") or f"QA_{item.get('question_number', len(output) + 1):04d}"

        if not question or not answer:
            continue

        output.append({
            "chunk_id": chunk_id,
            "category": category,
            "module": category,
            "question": question,
            "question_number": item.get("question_number", 0),
            "answer": answer,
            "retrieval_text": f"Category: {category}\nQuestion: {question}",
            "text": f"Question: {question}\n\nAnswer:\n{answer}",
            "source_type": "qa",
            "source_file": item.get("source_file", "e-GP System Q&A.txt"),
        })

    return output

