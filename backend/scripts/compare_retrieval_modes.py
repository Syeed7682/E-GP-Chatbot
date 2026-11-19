
"""
e-GP Retrieval Mode Comparison and Descriptive Answer Evaluation

Evaluates:
1. CSV-only retrieval
2. Embedding-only retrieval
3. Hybrid CSV + Embedding retrieval

Features:
- 10 uncommon e-GP questions
- Top-K retrieval configuration
- Descriptive, structured answer generation
- Retrieved evidence and source references
- Evidence assessment
- Offline/online LLM support
- Retrieval coverage comparison
- TXT evaluation report
"""

from __future__ import annotations

import sys
import os
from pathlib import Path


# ============================================================
# 1. PROJECT CONFIGURATION
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent

sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.services.embedding_service import embedding_service
from app.services.faiss_service import faiss_service
from app.services.qa_service import QAService
from app.services.llm_service import llm_service
from app.services.retrieval_service import (
    RetrievalService,
    retrieval_service,
)


TOP_K = 2

OFFLINE_ONLY = os.getenv(
    "COMPARE_OFFLINE_ONLY", ""
).lower() in {"1", "true", "yes"}


# ============================================================
# 2. TEST QUESTIONS
# ============================================================

QUESTIONS = [
    "How is a tenderer's beneficial ownership verified during e-GP registration?",

    "What happens when a procuring entity needs to revise a debarment decision after a court petition?",

    "How does the e-GP system handle a significantly low-priced responsive tender?",

    "Which workflow action is required after an approver approves a file before publication?",

    "How are external committee members selected from the Same PE and From External tabs?",

    "What information must be entered before an invoice can be forwarded to the AG?",

    "How does the system treat tender security validity when the proposal validity period changes?",

    "What is the process for configuring Tender Evaluation Report 1 and Tender Evaluation Report 2?",

    "How are pending bills loaded after selecting DDO and fiscal year in the iBAS integration?",

    "What does the Debarred Tenderer List record after a 42-day suspension decision?",
]


# ============================================================
# 3. EMPTY SERVICES
# ============================================================

class EmptyQA:
    """Disables Q&A retrieval for embedding-only evaluation."""

    def search(self, question: str, limit: int = 3):
        return []


class EmptyFaiss:
    """
    Prevents CSV-only retrieval from falling through
    to the manual FAISS index.
    """

    index = None
    metadata = []

    def load(self):
        return False


# ============================================================
# 4. RETRIEVAL COVERAGE
# ============================================================

def coverage(question: str, text: str) -> float:
    """
    Measures the percentage of question keywords
    appearing in the retrieved evidence.

    This is a diagnostic metric, not semantic accuracy.
    """

    words = {
        word.lower().strip(".,?!:;()")
        for word in question.split()
        if len(word.strip(".,?!:;()")) > 4
    }

    if not words:
        return 0.0

    lowered = text.lower()

    matched = sum(
        word in lowered
        for word in words
    )

    return matched / len(words)


# ============================================================
# 5. STRUCTURED ANSWER GENERATION INSTRUCTIONS
# ============================================================

def build_generation_prompt(question: str) -> str:

    return f"""
You are an expert assistant for the Bangladesh e-GP
(Electronic Government Procurement) System.

Your task is to answer the user's question using
ONLY the retrieved documentation.

USER QUESTION:
{question}

ANSWER GENERATION RULES:

1. Answer the exact question.
2. Use only the provided retrieved evidence.
3. Never invent procedures, requirements, menu names,
   deadlines, or system behavior.
4. Do not answer unrelated questions.
5. Start with a direct answer.
6. Explain the process descriptively.
7. Use numbered steps if the evidence describes a procedure.
8. Include relevant conditions and exceptions.
9. If multiple sources disagree, identify the discrepancy.
10. If evidence is insufficient, clearly state that.
11. Do not use general knowledge to fill missing information.

REQUIRED ANSWER STRUCTURE:

### 1. Direct Answer
Provide a concise and direct response.

### 2. Detailed Explanation
Explain the relevant system functionality,
requirements, or process.

### 3. Step-by-Step Process / Key Requirements
Use numbered steps or bullet points when supported
by the retrieved evidence.

If no procedure is available, write:
"No specific step-by-step procedure was identified
in the retrieved documentation."

### 4. Important Notes
Mention relevant conditions, limitations,
exceptions, or additional requirements.

### 5. Evidence Assessment
Choose one:
- Fully Supported
- Partially Supported
- Insufficient Evidence

Explain the reason briefly.

IMPORTANT:
The retrieved documentation is the only source of truth.
If the documentation does not answer the question,
do not generate an assumed answer.
"""


# ============================================================
# 6. SOURCE REFERENCE FORMATTER
# ============================================================

def format_source_reference(
    source: dict,
    rank: int,
) -> str:

    source_name = source.get("source", "Unknown")
    page = source.get("page", "N/A")
    score = source.get("score", "N/A")
    module = source.get("module", "N/A")
    question_id = source.get("question_id", "N/A")

    snippet = " ".join(
        source.get("snippet", "").split()
    )

    return (
        f"\n{rank}. SOURCE REFERENCE\n"
        f"   Document: {source_name}\n"
        f"   Page: {page}\n"
        f"   Module: {module}\n"
        f"   Question ID: {question_id}\n"
        f"   Relevance Score: {score}\n"
        f"   Retrieved Evidence: {snippet[:500]}\n"
    )


# ============================================================
# 7. EVIDENCE ASSESSMENT
# ============================================================

def assess_evidence(
    context: str,
    answer: str,
) -> str:

    if not context.strip():
        return "INSUFFICIENT EVIDENCE"

    insufficient_phrases = [
        "does not provide sufficient information",
        "insufficient information",
        "cannot determine from the provided",
        "not available in the retrieved",
    ]

    answer_lower = answer.lower()

    if any(
        phrase in answer_lower
        for phrase in insufficient_phrases
    ):
        return "INSUFFICIENT EVIDENCE"

    # This is intentionally conservative.
    # Actual answer grounding requires manual validation
    # or a separate semantic evaluation method.

    return "REQUIRES MANUAL VALIDATION"


# ============================================================
# 8. RETRIEVAL AND ANSWER GENERATION
# ============================================================

def run_mode(
    name: str,
    service: RetrievalService,
    question: str,
) -> dict:

    try:

        # --------------------------------------------
        # STEP 1: RETRIEVE DOCUMENTATION
        # --------------------------------------------

        context, sources = service.retrieve(
            question,
            top_k=TOP_K,
            use_keyword_search=name != "Embedding-only",
        )

        best_coverage = max(
            (
                coverage(
                    question,
                    source.get("snippet", ""),
                )
                for source in sources
            ),
            default=0.0,
        )

        # --------------------------------------------
        # STEP 2: GENERATE DESCRIPTIVE ANSWER
        # --------------------------------------------

        if context.strip() and sources:

            generation_prompt = build_generation_prompt(
                question
            )

            if OFFLINE_ONLY:

                answer = (
                    llm_service._offline_answer_generator(
                        generation_prompt,
                        context,
                    )
                )

                answer_model = "Offline grounded synthesis"
                was_offline = True

            else:

                (
                    answer,
                    answer_model,
                    was_offline,
                ) = llm_service.generate_answer_with_metadata(
                    generation_prompt,
                    context,
                    language="en",
                )

            evidence_status = assess_evidence(
                context,
                answer,
            )

        else:

            answer = """
### 1. Direct Answer

The retrieved documentation does not provide
sufficient information to answer this question.

### 2. Detailed Explanation

No relevant evidence was retrieved.

### 3. Step-by-Step Process / Key Requirements

Not available.

### 4. Important Notes

The question requires further documentation
or an improved retrieval strategy.

### 5. Evidence Assessment

INSUFFICIENT EVIDENCE
"""

            answer_model = "Not generated"
            was_offline = True
            evidence_status = "INSUFFICIENT EVIDENCE"

        # --------------------------------------------
        # STEP 3: RETURN EVALUATION RESULTS
        # --------------------------------------------

        return {
            "mode": name,
            "status": "available",
            "sources": sources,
            "coverage": best_coverage,
            "context": context,
            "answer": answer,
            "answer_model": answer_model,
            "was_offline": was_offline,
            "evidence_status": evidence_status,
        }

    except Exception as error:

        return {
            "mode": name,
            "status": f"error: {error}",
            "sources": [],
            "coverage": 0.0,
            "context": "",
            "answer": "Answer generation failed.",
            "answer_model": "none",
            "was_offline": True,
            "evidence_status": "NOT EVALUATED",
        }


# ============================================================
# 9. REPORT HEADER
# ============================================================

def build_report_header(
    csv_path: Path,
    csv_available: bool,
    semantic_available: bool,
) -> list[str]:

    report = [
        "e-GP RETRIEVAL MODE COMPARISON REPORT",
        "=" * 90,
        "",
        "PROJECT: e-GP Manual Chatbot",
        "EVALUATION: Retrieval and Descriptive Answer Generation",
        "",
        "TEST CONFIGURATION",
        "-" * 40,
        f"Questions Tested: {len(QUESTIONS)}",
        f"Retrieval Top-K: {TOP_K}",
        f"FAISS Metadata Records: {len(faiss_service.metadata)}",
        f"Configured CSV Path: {csv_path}",
        f"CSV Available: {'YES' if csv_available else 'NO'}",
        f"Semantic Embedding Available: {'YES' if semantic_available else 'NO'}",
        f"Offline Generation: {'YES' if OFFLINE_ONLY else 'NO'}",
        "",
    ]

    if not csv_available:
        report.extend([
            "WARNING:",
            "CSV file unavailable. CSV-only and Hybrid modes "
            "cannot be fully evaluated.",
            "",
        ])

    if not semantic_available:
        report.extend([
            "WARNING:",
            "Semantic embedding provider unavailable. "
            "Embedding-only mode will not be scored.",
            "",
        ])

    return report


# ============================================================
# 10. MAIN EVALUATION
# ============================================================

def main() -> int:

    print("\nStarting e-GP Retrieval Evaluation...")
    print("=" * 60)

    # --------------------------------------------
    # LOAD FAISS INDEX
    # --------------------------------------------

    if not faiss_service.load():
        raise RuntimeError(
            "The legacy FAISS index could not be loaded."
        )

    print(
        f"FAISS loaded: {len(faiss_service.metadata)} records"
    )

    # --------------------------------------------
    # INITIALIZE RETRIEVAL MODES
    # --------------------------------------------

    csv_path = Path(settings.EGP_EVAL_CSV)

    csv_available = csv_path.is_file()

    semantic_available = (
        embedding_service.semantic_search_available
    )

    # Embedding-only
    embedding_only = RetrievalService(
        emb_service=embedding_service,
        f_service=faiss_service,
        q_service=EmptyQA(),
        csv_q_service=None,
    )

    # CSV-only
    csv_only = RetrievalService(
        emb_service=embedding_service,
        f_service=EmptyFaiss(),
        q_service=EmptyQA(),
        csv_q_service=(
            QAService(csv_path=csv_path)
            if csv_available
            else None
        ),
    )

    # Hybrid uses production retrieval service
    hybrid = retrieval_service

    modes = [
        ("CSV-only", csv_only if csv_available else None),
        (
            "Embedding-only",
            embedding_only if semantic_available else None,
        ),
        (
            "Hybrid CSV+embedding",
            hybrid if csv_available else None,
        ),
    ]

    scores = {
        name: []
        for name, _ in modes
    }

    report = build_report_header(
        csv_path,
        csv_available,
        semantic_available,
    )
    report_header = report.copy()
    evaluations = []

    # --------------------------------------------
    # RUN ALL QUESTIONS
    # --------------------------------------------

    for number, question in enumerate(
        QUESTIONS,
        start=1,
    ):

        print(
            f"\nEvaluating Question {number}/{len(QUESTIONS)}..."
        )

        report.extend([
            "",
            "=" * 90,
            f"QUESTION {number}: {question}",
            "=" * 90,
        ])

        question_evaluations = {}

        for mode_name, service in modes:

            report.extend([
                "",
                f"RETRIEVAL MODE: {mode_name}",
                "-" * 70,
            ])

            if service is None:

                reason = (
                    "Required CSV file unavailable"
                    if mode_name != "Embedding-only"
                    else "Semantic embedding provider unavailable"
                )

                report.append(
                    f"STATUS: NOT RUN ({reason})"
                )

                question_evaluations[mode_name] = {
                    "status": "not run",
                    "reason": reason,
                    "sources": [],
                    "coverage": 0.0,
                    "answer": "Not generated because this retrieval mode was unavailable.",
                    "answer_model": "none",
                    "was_offline": True,
                    "evidence_status": "NOT EVALUATED",
                    "context": "",
                }

                continue

            result = run_mode(
                mode_name,
                service,
                question,
            )

            if result["status"] != "available":

                report.append(
                    f"STATUS: {result['status']}"
                )

                question_evaluations[mode_name] = result

                continue

            question_evaluations[mode_name] = result

            scores[mode_name].append(
                result["coverage"]
            )

            report.extend([
                "STATUS: SUCCESS",
                f"Best Term Coverage: {result['coverage']:.2f}",
                f"Retrieved Sources: {len(result['sources'])}",
            ])

            # --------------------------------
            # RETRIEVED SOURCE REFERENCES
            # --------------------------------

            report.extend([
                "",
                "RETRIEVED EVIDENCE AND SOURCE REFERENCES",
                "-" * 50,
            ])

            if result["sources"]:

                for rank, source in enumerate(
                    result["sources"],
                    start=1,
                ):

                    report.append(
                        format_source_reference(
                            source,
                            rank,
                        )
                    )

            else:

                report.append(
                    "No relevant sources retrieved."
                )

            # --------------------------------
            # DESCRIPTIVE ANSWER
            # --------------------------------

            report.extend([
                "",
                "GENERATED DESCRIPTIVE ANSWER",
                "-" * 50,
                result["answer"],
            ])

            # --------------------------------
            # ANSWER EVALUATION
            # --------------------------------

            report.extend([
                "",
                "ANSWER EVALUATION",
                "-" * 50,
                f"Generation Model: {result['answer_model']}",
                f"Offline Generation: {result['was_offline']}",
                f"Evidence Assessment: {result['evidence_status']}",
            ])

            # --------------------------------
            # RAW CONTEXT FOR DEBUGGING
            # --------------------------------

            report.extend([
                "",
                "RAW RETRIEVED CONTEXT",
                "-" * 50,
                result["context"] or "No context available.",
            ])

            print(
                f"  {mode_name}: "
                f"Coverage={result['coverage']:.2f}, "
                f"Sources={len(result['sources'])}"
            )

        evaluations.append((number, question, question_evaluations))

    # ========================================================
    # 11. FINAL COMPARISON SUMMARY
    # ========================================================

    ordered_report = list(report_header)
    for number, question, question_evaluations in evaluations:
        ordered_report.extend([
            "",
            "=" * 90,
            f"QUESTION {number}: {question}",
            "=" * 90,
        ])

        for mode_name in ("CSV-only", "Embedding-only", "Hybrid CSV+embedding"):
            result = question_evaluations.get(mode_name, {})
            ordered_report.extend([
                "",
                f"{mode_name.upper()} ANSWER",
                "-" * 70,
                f"Status: {result.get('status', 'not evaluated')}",
                f"Answer model: {result.get('answer_model', 'none')}",
                f"Answer:\n{result.get('answer', 'No answer generated.')}",
                "",
                "SOURCE / DOCUMENT / PAGE / RETRIEVAL EVIDENCE",
                "-" * 70,
            ])

            sources = result.get("sources", [])
            if sources:
                for rank, source in enumerate(sources, start=1):
                    ordered_report.append(format_source_reference(source, rank))
            else:
                ordered_report.append("No relevant sources retrieved.")

            ordered_report.extend([
                f"Best term coverage: {result.get('coverage', 0.0):.2f}",
                "Retrieved evidence:",
                result.get("context", "") or "No context available.",
            ])

        ordered_report.extend([
            "",
            "QUESTION COMPARISON",
            "-" * 70,
        ])
        ranked = sorted(
            ((name, data.get("coverage", 0.0)) for name, data in question_evaluations.items()),
            key=lambda item: item[1],
            reverse=True,
        )
        ordered_report.append(
            "Ranking by best-term coverage: "
            + " > ".join(f"{name} ({score:.2f})" for name, score in ranked)
        )
        ordered_report.append(
            "Comparison note: term coverage measures retrieval overlap; inspect the answers and evidence for factual completeness."
        )

    report = ordered_report
    report.extend([
        "",
        "",
        "=" * 90,
        "OVERALL RETRIEVAL PERFORMANCE SUMMARY",
        "=" * 90,
        "",
        "COMPARATIVE RESULTS",
        "-" * 50,
    ])

    summary_values = {}

    for mode_name, _ in modes:

        values = scores[mode_name]

        if values:

            average = sum(values) / len(values)

            summary_values[mode_name] = average

            report.append(
                f"{mode_name}: "
                f"Tested={len(values)}/{len(QUESTIONS)} | "
                f"Average Best-Term Coverage={average:.2f}"
            )

        else:

            summary_values[mode_name] = None

            report.append(
                f"{mode_name}: Tested=0/{len(QUESTIONS)}"
            )

    # --------------------------------------------
    # BEST RETRIEVAL MODE
    # --------------------------------------------

    valid_scores = {
        name: score
        for name, score in summary_values.items()
        if score is not None
    }

    if valid_scores:

        best_mode = max(
            valid_scores,
            key=valid_scores.get,
        )

        report.extend([
            "",
            f"Highest Average Term Coverage: {best_mode}",
            f"Coverage Score: {valid_scores[best_mode]:.2f}",
        ])

    # --------------------------------------------
    # INTERPRETATION
    # --------------------------------------------

    report.extend([
        "",
        "INTERPRETATION AND KEY FINDINGS",
        "-" * 50,
        "",
        "1. Retrieval Performance:",
        "   Compare the retrieved sources and term coverage "
        "across all available retrieval modes.",
        "",
        "2. Contextual Relevance:",
        "   Check whether the retrieved evidence actually "
        "addresses the user's question.",
        "",
        "3. Answer Generation:",
        "   Evaluate whether the LLM produces a descriptive "
        "answer based on the retrieved evidence.",
        "",
        "4. Grounding:",
        "   Identify answers that introduce unsupported "
        "information or answer unrelated questions.",
        "",
        "5. Fallback Mechanism:",
        "   Check whether the system correctly handles "
        "questions with insufficient retrieved evidence.",
        "",
        "RECOMMENDED R&D IMPROVEMENTS",
        "-" * 50,
        "",
        "- Optimize Top-K retrieval selection.",
        "- Evaluate embedding and reranking performance.",
        "- Improve context-to-answer grounding.",
        "- Investigate irrelevant retrieval results.",
        "- Implement evidence-based fallback responses.",
        "- Compare CSV, PDF, and embedding-based retrieval.",
        "- Validate answers using a smaller controlled dataset.",
        "- Conduct manual evaluation of factual correctness.",
        "",
        "EVALUATION LIMITATIONS",
        "-" * 50,
        "",
        "- Term coverage is not a semantic relevance metric.",
        "- Retrieval scores may not be comparable across modes.",
        "- Evidence assessment requires manual validation.",
        "- Answer quality must be evaluated separately "
        "from retrieval quality.",
        "- A retrieved source does not guarantee a correct answer.",
        "",
        "END OF REPORT",
    ])

    # ========================================================
    # 12. SAVE REPORT
    # ========================================================

    output_dir = ROOT_DIR / "documents"

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir / "RETRIEVAL_COMPARISON_REPORT.txt"
    )

    output_path.write_text(
        "\n".join(report) + "\n",
        encoding="utf-8",
    )

    print("\n" + "=" * 60)
    print("EVALUATION COMPLETED")
    print("=" * 60)

    print(f"Questions Evaluated: {len(QUESTIONS)}")
    print(f"Top-K: {TOP_K}")

    for mode_name, score in summary_values.items():

        if score is not None:
            print(
                f"{mode_name}: Average Coverage = {score:.2f}"
            )
        else:
            print(f"{mode_name}: Not evaluated")

    print(f"\nReport saved successfully:\n{output_path}")

    return 0


# ============================================================
# 13. EXECUTION
# ============================================================

if __name__ == "__main__":
    raise SystemExit(main())
