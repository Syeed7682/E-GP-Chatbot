"""System prompt for the e-GP Manual Multimodal Assistant."""
import os

_PROMPT_TXT_PATH = os.path.join(os.path.dirname(__file__), "system_prompt.txt")

def get_system_prompt() -> str:
    """Returns the official system prompt from system_prompt.txt or fallback."""
    if os.path.exists(_PROMPT_TXT_PATH):
        try:
            with open(_PROMPT_TXT_PATH, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return """You are Proca, an expert AI assistant for the Bangladesh e-GP (Electronic Government Procurement) system.
Always provide a clear, descriptive, and helpful answer in your own words synthesized from the retrieved context.
If no answer is found, clearly state that you couldn't find the answer in the official records and suggest contacting the e-GP Helpdesk (Hotline: 16575, Phone: +880 9609112233, Email: helpdesk@eprocure.gov.bd, Portal: https://eprocure.gov.bd).
"""
