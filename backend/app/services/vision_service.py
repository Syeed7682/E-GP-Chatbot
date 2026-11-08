"""
Vision Service (app/services/vision_service.py).
Extracts text, portal field names, and error dialogs from uploaded screenshots.
"""
import io
import re
import base64
from typing import Optional, Dict, Any

class VisionService:
    def __init__(self):
        self._ocr = None

    def extract_text_from_base64(self, image_base64: str) -> str:
        """Extracts text from base64 image data using OCR."""
        if not image_base64:
            return ""

        try:
            # Clean base64 string
            clean_b64 = re.sub(r'^data:image\/[a-z]+;base64,', '', image_base64.strip())
            img_bytes = base64.b64decode(clean_b64)
            
            # Try PaddleOCR if available
            try:
                import importlib
                paddle_mod = importlib.import_module("paddleocr")
                PaddleOCR = getattr(paddle_mod, "PaddleOCR")
                if self._ocr is None:
                    self._ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
                result = self._ocr.ocr(img_bytes, cls=True)
                lines = []
                for res in result:
                    if res:
                        for line in res:
                            lines.append(line[1][0])
                return "\n".join(lines).strip()
            except Exception:
                pass

            # Try pytesseract / PIL
            try:
                import importlib
                from PIL import Image
                pytesseract = importlib.import_module("pytesseract")
                img = Image.open(io.BytesIO(img_bytes))
                text = pytesseract.image_to_string(img)
                return text.strip()
            except Exception:
                pass

        except Exception as e:
            print(f"[vision_service] OCR extraction notice: {e}")

        return ""

vision_service = VisionService()

