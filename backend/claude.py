import os
import anthropic
import fitz  # PyMuPDF
import base64
import time
import sys
from dotenv import load_dotenv

from helpers import pdf_to_images, encode_image, save_text_to_file

# Load API key from .env file
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def claude_extract(image_paths):
    """Send images to Claude API for OCR text extraction."""
    extracted_text = ""

    print("Beginning OCR text extraction via Claude API...")
    for i, image_path in enumerate(image_paths):
        base64_image = encode_image(image_path)
        
        print(f"Processing page {i + 1}...")

        try:
            response = client.messages.create(
                model="claude-3-opus-20240229",  # Adjust the model if needed
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all text from this image. Return only the extracted text, without any additional commentary."
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": base64_image,
                                },
                            },
                        ],
                    }
                ],
            )

            # Extract text from Claude response
            extracted_text += response.content[0].text + "\n\n"

        except Exception as e:
            print(f"Error during OCR extraction: {e}")
            continue

        time.sleep(2)  # Avoid rate limits

    return extracted_text


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
    if not ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY not found in environment variables")
        sys.exit(1)

    pdf_path = "testDoc.pdf"  # Hardcoded for now

    try:
        image_paths = pdf_to_images(pdf_path)
        extracted_text = claude_extract(image_paths)
        output_file = f"{os.path.splitext(pdf_path)[0]}_extracted.txt"
        save_text_to_file(extracted_text, output_file)
        print(f"OCR completed. Extracted text saved to {output_file}")
        cleanup_temp_files(image_paths)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()