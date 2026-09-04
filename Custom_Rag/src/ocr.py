from pathlib import Path
import pytesseract
from PIL import Image

def ocr_image(path: str) -> str:
    image = Image.open(path)
    return pytesseract.image_to_string(image).strip()

def ocr_available() -> bool:
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False
