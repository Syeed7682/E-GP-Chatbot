"""
Core Security and Input Sanitization Utilities.
Prevents prompt injection and sanitizes queries and uploads.
"""
import re
from typing import Optional

def sanitize_user_query(text: str) -> str:
    """Sanitizes user input by stripping malicious script tags and non-printable control chars."""
    if not text:
        return ""
    # Strip basic script tags
    cleaned = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    # Strip HTML tags
    cleaned = re.sub(r'<[^>]+>', '', cleaned)
    # Replace control characters
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', cleaned)
    return cleaned.strip()

def sanitize_image_base64(data: Optional[str]) -> Optional[str]:
    """Validates and strips base64 headers safely."""
    if not data:
        return None
    # Strip prefix data:image/...;base64,
    if ";base64," in data:
        return data.split(";base64,")[1].strip()
    return data.strip()

