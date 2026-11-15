"""
OCR Processor for e-GP Manual and Portal Screenshots.
Provides text extraction from images using PaddleOCR with Tesseract fallback.
"""
import io
import logging
from pathlib import Path
from typing import Optional
from PIL import Image

logger = logging.getLogger(__name__)

_PADDLE_OCR = None
_TESSERACT_AVAILABLE = None


def _get_paddle_ocr():
    global _PADDLE_OCR
    if _PADDLE_OCR is False:
        return None
    if _PADDLE_OCR is not None:
        return _PADDLE_OCR

    try:
        import importlib
        paddle_mod = importlib.import_module("paddleocr")
        paddle_cls = getattr(paddle_mod, "PaddleOCR")
        _PADDLE_OCR = paddle_cls(use_angle_cls=True, lang="en", show_log=False)
        return _PADDLE_OCR
    except Exception as e:
        logger.debug("PaddleOCR not available: %s", e)
        _PADDLE_OCR = False
        return None


def _get_pytesseract():
    import importlib
    try:
        return importlib.import_module("pytesseract")
    except Exception:
        return None


def _check_tesseract() -> bool:
    global _TESSERACT_AVAILABLE
    if _TESSERACT_AVAILABLE is not None:
        return _TESSERACT_AVAILABLE

    pytess = _get_pytesseract()
    if pytess is not None:
        try:
            pytess.get_tesseract_version()
            _TESSERACT_AVAILABLE = True
            return True
        except Exception:
            pass

    _TESSERACT_AVAILABLE = False
    return False


def process_ocr(image_input: str | Path | bytes | Image.Image) -> str:
    """
    Extracts text from an image using PaddleOCR or PyTesseract.
    Returns cleaned extracted text.
    """
    # Normalize image to PIL Image or numpy array
    pil_image = None
    if isinstance(image_input, (str, Path)):
        p = Path(image_input)
        if not p.exists():
            return ""
        pil_image = Image.open(p).convert("RGB")
    elif isinstance(image_input, bytes):
        pil_image = Image.open(io.BytesIO(image_input)).convert("RGB")
    elif isinstance(image_input, Image.Image):
        pil_image = image_input.convert("RGB")
    else:
        return ""

    # Try PaddleOCR
    ocr = _get_paddle_ocr()
    if ocr is not None:
        try:
            import numpy as np
            img_np = np.array(pil_image)
            result = ocr.ocr(img_np, cls=True)
            extracted_lines = []
            if result and result[0]:
                for line in result[0]:
                    text = line[1][0]
                    confidence = line[1][1]
                    if confidence > 0.4:
                        extracted_lines.append(text)
            if extracted_lines:
                return "\n".join(extracted_lines)
        except Exception as e:
            logger.debug("PaddleOCR execution error: %s", e)

    # Try Tesseract
    if _check_tesseract():
        pytess = _get_pytesseract()
        if pytess is not None:
            try:
                text = pytess.image_to_string(pil_image)
                return text.strip()
            except Exception as e:
                logger.debug("Tesseract execution error: %s", e)

    return ""

