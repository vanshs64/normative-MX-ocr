import os
import anthropic
import fitz  # PyMuPDF
import base64
import time
import sys
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def pdf_to_images(pdf_path):
    """Convert PDF pages to images."""
    temp_dir = "temp_images"
    os.makedirs(temp_dir, exist_ok=True)

    pdf_document = fitz.open(pdf_path)
    image_paths = []

    print("Converting PDF pages to images...")
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        zoom = 2  # Increase DPI
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        image_path = os.path.join(temp_dir, f"page_{page_num + 1}.png")
        pix.save(image_path)
        image_paths.append(image_path)

    return image_paths


def claude_extract(image_paths):
    """Send images to Claude API for OCR text extraction."""
    extracted_text = ""

    print("Beginning OCR text extraction via Claude API...")
    for i, image_path in enumerate(image_paths):
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

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
    if not ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY not found in environment variables")
        sys.exit(1)

    pdf_path = "testDoc.pdf"  # Hardcoded for now

    try:
        image_paths = pdf_to_images(pdf_path)
        extracted_text = claude_extract(image_paths)
        output_file = f"{os.path.splitext(pdf_path)[0]}_extracted.txt"
        save_text(extracted_text, output_file)
        print(f"OCR completed. Extracted text saved to {output_file}")
        cleanup_temp_files(image_paths)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
