import os
import fitz  # PyMuPDF
import base64
import requests
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import time

# Load API key from .env file
load_dotenv()
OPENAI_SECRET_KEY = os.getenv("OPENAI_SECRET_KEY")
OPENAI_API_KEY_V = os.getenv("OPENAI_API_KEY_V")

def pdf_to_images(pdf_path, output_folder="temp_images", dpi=300):
    """Convert PDF pages to images using PyMuPDF and save them as JPEG."""
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []
    
    for i, page in tqdm(enumerate(doc)):
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        image_path = os.path.join(output_folder, f"page_{i + 1}.jpg")
        img.save(image_path, "JPEG")
        image_paths.append(image_path)
    print("Completed PDF to image conversion.")
    return image_paths

def encode_image(image_path):
    """Encode image as Base64."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def openai_extract(image_paths):
    """Send images to OpenAI Vision API for OCR text extraction."""
    client = OpenAI(api_key=OPENAI_SECRET_KEY)

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

def save_text(output_text, output_file="extracted_text.txt"):
    """Save extracted text to a file."""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output_text)

def main():
    pdf_path = "Trig_Integrals.pdf"
    image_paths = pdf_to_images(pdf_path)
    extracted_text = openai_extract(image_paths)
    save_text(extracted_text)
    print(f"OCR completed. Extracted text saved to extracted_text.txt")

if __name__ == "__main__":
    main()
