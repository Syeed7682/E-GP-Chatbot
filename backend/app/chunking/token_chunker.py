"""
Token Chunker using BGE-M3 Tokenizer.
Measures chunk size in true token counts with configurable overlap.
Includes robust fallback for environments without local Hugging Face model cache.
"""
import re
from typing import List, Optional

_TOKENIZER = None
_TOKENIZER_FAILED = False


def _get_tokenizer():
    global _TOKENIZER, _TOKENIZER_FAILED
    if _TOKENIZER_FAILED or _TOKENIZER is not None:
        return _TOKENIZER

    try:
        from transformers import AutoTokenizer
        _TOKENIZER = AutoTokenizer.from_pretrained("BAAI/bge-m3", local_files_only=False)
        return _TOKENIZER
    except Exception:
        _TOKENIZER_FAILED = True
        return None


def chunk_text(text: str, chunk_size: int = 450, overlap: int = 60) -> List[str]:
    """
    Splits text into chunks of `chunk_size` tokens with `overlap` tokens.
    Uses BGE-M3 tokenizer when available, or word-based token approximation as fallback.
    """
    if not text or not text.strip():
        return []

    tokenizer = _get_tokenizer()
    if tokenizer is not None:
        try:
            tokens = tokenizer.encode(text, add_special_tokens=False)
            chunks: List[str] = []
            start = 0
            while start < len(tokens):
                end = min(start + chunk_size, len(tokens))
                chunk_tokens = tokens[start:end]
                chunk_str = tokenizer.decode(chunk_tokens, skip_special_tokens=True).strip()
                if chunk_str:
                    chunks.append(chunk_str)
                if end == len(tokens):
                    break
                start = end - overlap
            return chunks
        except Exception:
            pass

    # Word/Subword heuristic fallback (approx 1 token = 0.75 words, so chunk_size tokens ~= chunk_size * 0.75 words)
    words = re.findall(r"\S+", text)
    if not words:
        return []

    word_chunk_size = max(int(chunk_size * 0.75), 10)
    word_overlap = max(int(overlap * 0.75), 2)

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + word_chunk_size, len(words))
        chunk_str = " ".join(words[start:end]).strip()
        if chunk_str:
            chunks.append(chunk_str)
        if end == len(words):
            break
        start = end - word_overlap

    return chunks

