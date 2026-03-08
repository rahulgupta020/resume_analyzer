# analyzer/utils.py
import io
import pytesseract
from PIL import Image
from pdfminer.high_level import extract_text # Added for PDF support

def get_raw_text(file):
    """
    Detects file type and extracts text from PDF or Image
    """
    extension = file.name.split('.')[-1].lower()
    
    # --- PDF EXTRACTION ---
    if extension == 'pdf':
        try:
            # pdfminer reads the file stream and returns raw text
            return extract_text(io.BytesIO(file.read()))
        except Exception as e:
            print(f"PDF Error: {e}")
            return ""

    # --- IMAGE OCR (Existing) ---
    elif extension in ['jpg', 'jpeg', 'png']:
        try:
            return pytesseract.image_to_string(Image.open(file))
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
            
    return ""