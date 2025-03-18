import os
import fitz  # PyMuPDF
import base64
import requests
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import time

from helpers import pdf_to_images, encode_image, save_text_to_file

# Load API key from .env file
load_dotenv()
OPENAI_SECRET_KEY = os.getenv("OPENAI_SECRET_KEY")
OPENAI_SECRET_KEY_2 = os.getenv("OPENAI_SECRET_KEY_2")

def openai_extract(image_paths):
    """Send images to OpenAI Vision API for OCR text extraction."""
    client = OpenAI(api_key=OPENAI_SECRET_KEY_2)

    extracted_text = ""
    
    print("Beginning OCR text extraction via API...")
    for image_path in tqdm(image_paths):
        base64_image = encode_image(image_path)
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "user", "content": [
                    {"type": "input_text", "text": "Extract all text from this image."},
                    {"type": "input_image", "image_url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}
                ]}
            ]
        )
        extracted_text += response.output_text + "\n\n"
        time.sleep(1)  # wait for 1 second between requests to avoid quota exceeding
    
    return extracted_text

def main():
    pdf_path = "Trig_Integrals.pdf"
    image_paths = pdf_to_images(pdf_path)
    extracted_text = openai_extract(image_paths)
    save_text_to_file(extracted_text)
    print(f"OCR completed. Extracted text saved to extracted_text.txt")

if __name__ == "__main__":
    main()
