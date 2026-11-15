"""
Table Extractor for e-GP Manual.
Extracts tabular structures, preserving column headings and row relationships.
Specialized for procurement fee schedules, thresholds, and committee matrices.
"""
import re
from typing import Any, Dict, List, Optional


def extract_tables_from_text(page_text: str, page_num: int) -> List[Dict[str, Any]]:
    """
    Heuristically extracts tabular text blocks from extracted page text.
    Detects pipe-delimited, tab-delimited, or multi-space aligned rows.
    """
    tables: List[Dict[str, Any]] = []
    lines = page_text.splitlines()

    table_lines: List[str] = []
    in_table = False

    for line in lines:
        stripped = line.strip()
        # Check if line looks like a table row (contains | or multiple tabs/col delimiters)
        if "|" in stripped or "\t" in stripped or re.search(r"\s{4,}", stripped):
            parts = [p.strip() for p in re.split(r"[|\t]|\s{4,}", stripped) if p.strip()]
            if len(parts) >= 2:
                table_lines.append(stripped)
                in_table = True
                continue

        if in_table:
            if len(table_lines) >= 2:
                tables.append({
                    "page": page_num,
                    "raw_lines": table_lines.copy(),
                    "markdown": _format_as_markdown_table(table_lines),
                })
            table_lines.clear()
            in_table = False

    if in_table and len(table_lines) >= 2:
        tables.append({
            "page": page_num,
            "raw_lines": table_lines.copy(),
            "markdown": _format_as_markdown_table(table_lines),
        })

    return tables


def _format_as_markdown_table(lines: List[str]) -> str:
    """Formats raw table lines into valid Markdown table syntax."""
    rows: List[List[str]] = []
    max_cols = 0

    for line in lines:
        cols = [c.strip() for c in re.split(r"[|\t]|\s{4,}", line) if c.strip()]
        if cols:
            rows.append(cols)
            if len(cols) > max_cols:
                max_cols = len(cols)

    if not rows or max_cols < 2:
        return "\n".join(lines)

    # Pad rows to max_cols
    for r in rows:
        while len(r) < max_cols:
            r.append("")

    header = "| " + " | ".join(rows[0]) + " |"
    separator = "| " + " | ".join(["---"] * max_cols) + " |"
    body = ["| " + " | ".join(r) + " |" for r in rows[1:]]

    return "\n".join([header, separator] + body)


def extract_tables_from_page(fitz_page, page_num: int) -> List[Dict[str, Any]]:
    """
    Extracts tables using PyMuPDF's built-in table finder (fitz.Page.find_tables()) if available.
    Falls back to text heuristic extraction.
    """
    tables: List[Dict[str, Any]] = []

    if hasattr(fitz_page, "find_tables"):
        try:
            tab_finder = fitz_page.find_tables()
            for tab in tab_finder.tables:
                extracted = tab.extract()
                if extracted and len(extracted) >= 2:
                    header = [str(c or "").strip() for c in extracted[0]]
                    body_rows = [[str(c or "").strip() for c in row] for row in extracted[1:]]
                    md = "| " + " | ".join(header) + " |\n"
                    md += "| " + " | ".join(["---"] * len(header)) + " |\n"
                    for r in body_rows:
                        md += "| " + " | ".join(r) + " |\n"

                    tables.append({
                        "page": page_num,
                        "header": header,
                        "rows": body_rows,
                        "markdown": md.strip(),
                        "bbox": tab.bbox,
                    })
        except Exception:
            pass

    if not tables:
        text = fitz_page.get_text("text")
        tables = extract_tables_from_text(text, page_num)

    return tables

