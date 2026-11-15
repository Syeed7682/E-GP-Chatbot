"""
Table Chunker for e-GP Manual.
Transforms structured table records into highly retrievable chunks with repeating headers.
Ensures procurement fee tables, thresholds, and matrices are search-optimized.
"""
from typing import Any, Dict, List


def chunk_table(
    table_record: Dict[str, Any],
    section: str = "Tender Document Fees & Conditions",
    document_id: str = "EGP_MANUAL_V1",
    source_file: str = "egp_manual.pdf",
    chunk_index: int = 1,
) -> Dict[str, Any]:
    """
    Transforms a table record into a structured chunk with repeating column headers.
    """
    page_num = table_record.get("page", 1)
    header = table_record.get("header", [])
    rows = table_record.get("rows", [])
    raw_md = table_record.get("markdown", "")

    header_line = " | ".join(header) if header else "Column Data"
    row_strings = []

    for r in rows:
        row_str = " | ".join(str(c) for c in r)
        row_strings.append(f"{header_line} ==> {row_str}")

    expanded_text = f"Section: {section}\nPage: {page_num}\nTable Structure:\n" + "\n".join(row_strings)
    if raw_md:
        expanded_text += f"\n\nMarkdown Table:\n{raw_md}"

    chunk_id = f"TABLE_{page_num:04d}_{chunk_index:02d}"

    return {
        "chunk_id": chunk_id,
        "parent_id": f"SECTION_TABLE_P{page_num}",
        "document_id": document_id,
        "page_start": page_num,
        "page_end": page_num,
        "section": section,
        "content_type": "table",
        "text": expanded_text,
        "table_markdown": raw_md,
        "header": header,
        "source": source_file,
        "source_type": "table",
    }

