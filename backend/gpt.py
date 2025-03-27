import os
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv
import time

import ast

from helpers import pdf_to_images, encode_image, save_text_to_file

# Load API key from .env file
load_dotenv()
OPENAI_SECRET_KEY = os.getenv("OPENAI_SECRET_KEY")

def openai_extract(image_paths, pdf_name):
    """Send images to OpenAI Vision API for OCR text extraction."""
    client = OpenAI(api_key=OPENAI_SECRET_KEY)

    expectation_key = []
    # Construct the absolute path to the file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.abspath(os.path.join(current_dir, "..", "test_docs", "truths", "T1John.txt"))

    with open(file_path, "r") as f:
        truths_dict = ast.literal_eval(f.read())  # Assuming the file contains a dictionary in string format
        expectation_key = list(truths_dict.keys())
        
        
    extracted_text = ""
    
    print("Beginning OCR text extraction via API...")
    for image_path in tqdm(image_paths):
        base64_image = encode_image(image_path)
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "user", "content": [
                    {f"type": "input_text", "text": "Extract all text from this image. Please expect to find the mapping between key-value pairs given through these extracted data dictionary keys: {expectation_key}. Please return a value pair for each of these in a similar dictionary format."},
                    {"type": "input_image", "image_url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}
                ]}
            ]
        )
        extracted_text += response.output_text + "\n\n"
        time.sleep(1)  # wait for 1 second between requests to avoid quota exceeding
    
    return extracted_text

def main():
    pdf_name = "T1John.pdf"
    pdf_path = f"../test_docs/{pdf_name}"

    image_paths = pdf_to_images(pdf_path, "JPEG")
    extracted_text = openai_extract(image_paths, "T1John.txt")
    save_text_to_file(extracted_text, "extracted_text.txt")
    print(f"OCR completed. Extracted text saved to extracted_text.txt")

if __name__ == "__main__":
    main()
