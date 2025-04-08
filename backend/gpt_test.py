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

def openai_extract(image_paths):
    """Send images to OpenAI Vision API for OCR text extraction from multiple pages, batched intelligently."""
    client = OpenAI(api_key=OPENAI_SECRET_KEY)

    # Load the expected keys from the truth file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    file_path = os.path.abspath(os.path.join(current_dir, "..", "test_docs", "test_study_data", "BobRef", "T4BobRef.txt"))

    with open(file_path, "r") as f:
        truths_dict = ast.literal_eval(f.read())
        expectation_keys = list(truths_dict.keys())

    # Encode all images
    image_inputs = []
    for image_path in image_paths:
        base64_image = encode_image(image_path)
        image_inputs.append({
            "type": "input_image",
            "image_url": f"data:image/jpeg;base64,{base64_image}",
            "detail": "high"
        })

    print("Sending all images in one batch to OpenAI Vision API...")

    # Create a single prompt
    prompt = [
        {
            "type": "input_text",
            "text": (
                "You will be given multiple pages of a document as images. "
                "Extract text and find the best possible values for the following keys: "
                f"{expectation_keys}. They may not appear on the same page, but do your best "
                "to find and return a final dictionary containing these key-value pairs. "
                "Do not include unrelated information or codeblock formatting, only the Dictionary."
            )
        }
    ] + image_inputs

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.output_text

def main():
    pdf_name = "T4Bob.pdf"
    pdf_path = f"../test_docs/test_study_data/Bob/{pdf_name}"

    image_paths = pdf_to_images(pdf_path, "JPEG")
    extracted_text = openai_extract(image_paths)
    
    print(extracted_text)

    save_text_to_file(extracted_text, f"../test_docs/test_study_data/BobHyp", f"T4BobGPTHyp.txt")
    print(f"OCR completed. Extracted text saved to extracted_text.txt")

if __name__ == "__main__":
    main()
