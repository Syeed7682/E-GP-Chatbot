"""
Script to cover all uncovered questions in egp_contractor_evaluation_dataset.csv.
Provides official grounded answers, sections, pages, citations, and notes
based on official e-GP manual, e-GP Master Q&A (1,000 solutions),
Public Procurement Act 2006, and Public Procurement Rules 2008 (PPR-2008).
"""
import csv
import re
from typing import Dict, Any, Optional

def normalize_key(q: str) -> str:
    """Normalizes question string to find canonical topic key."""
    s = q.strip().lower()
    s = re.sub(r'^(please explain:\s*|as a tenderer,\s*|i am a contractor\.\s*)', '', s)
    s = re.sub(r'[?.,!;:"]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

print("Testing script setup...")
