import os
import base64
import time
import sys
import requests
import json
from dotenv import load_dotenv
from pdf2image import convert_from_path

# Load API key from .env file
load_dotenv()
GOOGLE_CLOUD_VISION_API_KEY = os.getenv("GOOGLE_CLOUD_VISION_API_KEY")

if not GOOGLE_CLOUD_VISION_API_KEY:
    print("Error: GOOGLE_CLOUD_VISION_API_KEY not found in environment variables")
    sys.exit(1)


def pdf_to_images(pdf_path):
    """Convert PDF pages to images."""
    temp_dir = "temp_images"
    os.makedirs(temp_dir, exist_ok=True)

    image_paths = []

    print("Converting PDF pages to images...")
    images = convert_from_path(pdf_path, dpi=300, output_folder=temp_dir, fmt="png")
    for i, image in enumerate(images):
        image_path = os.path.join(temp_dir, f"page_{i + 1}.png")
        image.save(image_path, "PNG")
        image_paths.append(image_path)

    return image_paths


def google_vision_extract(image_paths):
    """Send images to Google Cloud Vision API for OCR text extraction."""
    extracted_text = ""

    print("Starting OCR text extraction via Google Cloud Vision API...")

    for i, image_path in enumerate(image_paths):
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        print(f"Processing page {i + 1}...")

        url = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_CLOUD_VISION_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "requests": [
                {
                    "image": {"content": base64_image},
                    "features": [{"type": "TEXT_DETECTION"}],
                }
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                extracted_text += result["responses"][0].get("fullTextAnnotation", {}).get("text", "") + "\n\n"
            else:
                print(f"Error: API returned status code {response.status_code}")
                print(f"Response: {response.text}")

        except Exception as e:
            print(f"Error during OCR extraction: {e}")
            continue

        time.sleep(1)  # Avoid rate limits

    return extracted_text


def save_text(output_text, output_file="extracted_text.txt"):
    """Save extracted text to a file."""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output_text)


def cleanup_temp_files(image_paths):
    """Clean up temporary image files."""
    print("Cleaning up temporary files...")
    for path in image_paths:
        try:
            os.remove(path)
        except Exception as e:
            print(f"Error removing {path}: {e}")

    try:
        os.rmdir("temp_images")
    except Exception as e:
        print(f"Error removing temp directory: {e}")


def main():
    pdf_path = "testDoc.pdf"  # Change to your actual PDF file

    try:
        image_paths = pdf_to_images(pdf_path)
        extracted_text = google_vision_extract(image_paths)
        output_file = f"{os.path.splitext(pdf_path)[0]}_extracted.txt"
        save_text(extracted_text, output_file)
        print(f"OCR completed. Extracted text saved to {output_file}")
        cleanup_temp_files(image_paths)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
