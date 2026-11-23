"""Shared text cleanup for CSV and PDF retrieval indexes."""
import re
import unicodedata


def clean_text(value: str) -> str:
    """Remove extraction noise while preserving searchable document content."""
    text = unicodedata.normalize("NFKC", value or "")
    if any(marker in text for marker in ("â", "Ã", "Â", "ð")):
        try:
            repaired = text.encode("latin1").decode("utf-8")
            bad = sum(text.count(x) for x in ("â", "Ã", "Â", "ð"))
            fixed = sum(repaired.count(x) for x in ("â", "Ã", "Â", "ð"))
            if fixed < bad:
                text = repaired
        except UnicodeError:
            pass
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    text = "".join(ch for ch in text if ch in "\n\t" or unicodedata.category(ch)[0] != "C")
    return re.sub(r"\s+", " ", text).strip()
