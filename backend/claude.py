import os
import sys
import time
from anthropic import Anthropic
from dotenv import load_dotenv
from helpers import pdf_to_images, encode_image, save_text_to_file, cleanup_temp_files
from calculate_score import append_score_to_csv
from tqdm import tqdm

# Load API key from .env file
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Initialize Anthropic client
client = Anthropic(api_key=ANTHROPIC_API_KEY)

def claude_extract(image_paths, key_template):
    """Send images to Claude API for OCR text extraction."""
    extracted_text = ""

    image_inputs = []
    for image_path in image_paths:
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
                                    "media_type": "image/jpeg",
                                    "data": base64_image,
                                },
                            },
                        ],
                    }
                ],
            )

    # Extract text from Claude response
    extracted_text += response.content[0].text

    return extracted_text

def main():
    if not ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY not found in environment variables")
        sys.exit(1)
    #Hardcoded for now
    pdf_path = "T4Vansh.pdf"
    
    try:
        image_paths = pdf_to_images(pdf_path, "JPEG")
        extracted_text = claude_extract(image_paths)
        output_file = f"{os.path.splitext(pdf_path)[0]}_extracted.txt"
        save_text_to_file(extracted_text, output_file)

        print(f"OCR completed. Extracted text saved to {output_file}")

        cleanup_temp_files(image_paths)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

def main_old():

    # the three for now, add NOA in future
    doc_types = ["T1", "T4", "FS"]

    # Read names from the names.txt file
    names = []
    with open("../test_docs/names.txt", "r") as list_of_files:
        names = list_of_files.read().split()  # Put names into an array (iterable)

    # Process each name and document type
    for name in tqdm(names, desc="Processing Names"):
        for doc_type in doc_types:
            print(f"Starting extraction for {name}'s {doc_type}...")

            # Construct file paths
            file_name = f"{doc_type}{name}.pdf"
            pdf_path = f"../test_docs/test_study_data/{name}/{file_name}"
            template_path = f"../test_docs/templates/{doc_type}Template.txt"

            # Check if the PDF file exists
            if not os.path.exists(pdf_path):
                print(f"File not found: {pdf_path}")
                continue

            # Load the key template
            key_template = ""
            with open(template_path, "r") as f:
                key_template = f.read()

            # Convert PDF to images
            image_paths = pdf_to_images(pdf_path, "JPEG")

            extracted_text = openai_extract(image_paths, key_template)

            # indicate which hypothesis it is, in this case it is openai's "GPTHyp"
            save_text_to_file(extracted_text, f"../test_docs/test_study_data/{name}Hyp", f"{doc_type}{name}GPTHyp.txt")

            print(f"Extraction for {name}'s {doc_type} done.")

        append_score_to_csv(name,"CLAUDE")

        print(f"CER Score Calculation also complete for {name}")

    # Cleanup temporary files after processing each document
    temp_images_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "temp_images"))
    if os.path.exists(temp_images_dir):
        for file_name in os.listdir(temp_images_dir):
            file_path = os.path.join(temp_images_dir, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("Temporary images deleted.")
    else:
        print("Temporary images directory does not exist.")



if __name__ == "__main__":
    main()