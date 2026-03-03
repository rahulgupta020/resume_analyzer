# analyzer/utils.py
import pytesseract
from PIL import Image
import io

# If you are on Windows, you may need to point to the tesseract executable:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(file):
    """Extracts raw text from JPEG, PNG, or other image formats"""
    try:
        # Open the uploaded image file
        image = Image.open(file)
        # Perform OCR to get string data
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""