"""
Context Builder for Grounded Answer Synthesis.
Assembles verified manual passages, page citations, screen references, and tables
into structured context blocks for the LLM.
"""
from typing import Any, Dict, List, Tuple


def build_grounded_context(candidates: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]], List[str]]:
    """
    Constructs an authoritative context string and extracts citation sources.
    
    Args:
        candidates: List of top retrieved document dictionaries
        
    Returns:
        Tuple of (formatted_context_string, sources_list, portal_screens_list)
    """
    context_blocks: List[str] = []
    sources: List[Dict[str, Any]] = []
    portal_screens: List[str] = []
    seen_screens = set()

    for idx, doc in enumerate(candidates, start=1):
        source_type = doc.get("source_type", "pdf")
        page = doc.get("page_start") or doc.get("page", 1)
        section = doc.get("section") or doc.get("category") or "e-GP Guidelines"
        chunk_id = doc.get("chunk_id", f"C_{idx}")
        text = doc.get("text") or doc.get("content", "")
        screen_ref = doc.get("screen_reference") or doc.get("screen")
        score = float(doc.get("rerank_score", doc.get("rrf_score", doc.get("score", 0.0))))

        if screen_ref and screen_ref not in seen_screens:
            portal_screens.append(screen_ref)
            seen_screens.add(screen_ref)

        header = f"[Source {idx} | Page {page} | Section: {section}]"
        if screen_ref:
            header += f" [Checkpoint: {screen_ref}]"

        context_blocks.append(f"{header}\n{text}")

        # Build SourceDocument item
        snippet = text[:280].replace("\n", " ").strip()
        if len(text) > 280:
            snippet += "..."

        sources.append({
            "page": int(page),
            "chunk_id": str(chunk_id),
            "score": round(score, 3),
            "snippet": snippet,
            "screen_reference": screen_ref,
            "source": doc.get("source") or doc.get("source_file", "egp_manual.pdf"),
            "section": section,
            "source_type": source_type,
            "question_number": doc.get("question_number"),
            "module": doc.get("category") or doc.get("module"),
        })

    full_context = "\n\n---\n\n".join(context_blocks)
    return full_context, sources, portal_screens

