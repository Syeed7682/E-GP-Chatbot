"""
Document Parser Service (app/services/document_parser.py).
Parses section headers, screen references (e.g. Screen - D50), and tables from page text.
"""
import re
from typing import Dict, Any, List

class DocumentParser:
    @staticmethod
    def extract_screen_references(text: str) -> List[str]:
        """Extracts portal screen IDs like Screen - D50, Screen - Q10.4, Screen - C41.1."""
        matches = re.findall(r'(?:Screen|Figure)\s*[-–—:]\s*([A-Za-z0-9_.]+)', text, re.IGNORECASE)
        screens = []
        for m in matches:
            cleaned = f"Screen - {m.upper()}"
            if cleaned not in screens:
                screens.append(cleaned)
        return screens

    @staticmethod
    def extract_section_title(text: str, default_page: int) -> str:
        """Identifies primary section title or guideline heading."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:5]:
            # Look for numbered headings e.g. "4.1 Tender Creation" or "7.1 Debarment"
            if re.match(r'^\d+(\.\d+)+\s+[A-Za-z]', line):
                return line
            if line.isupper() and len(line) > 5 and len(line) < 80:
                return line
        return f"e-GP Manual Section (Page {default_page})"

document_parser = DocumentParser()

