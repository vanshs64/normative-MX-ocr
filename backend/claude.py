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

    # Prepare image inputs
    image_inputs = []
    for image_path in image_paths:
        base64_image = encode_image(image_path)
        image_inputs.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": base64_image,
                },
            }
        )

    # Prepare the prompt
    prompt_text = (
        "You will be given multiple pages of a document as images. "
        "Extract text and find the best possible values for the following keys: "
        f"{key_template}. They may not appear on the same page, but do your best "
        "to find and return a final dictionary containing these key-value pairs. "
        "Do not include unrelated information or codeblock formatting, only the Dictionary."
    )

    # Combine the text prompt and image inputs
    messages = [
        {"type": "text", "text": prompt_text}
    ] + image_inputs

    print("Sending all images in one batch to Claude Vision API...")

    # Send the request to the Claude API
    response = client.messages.create(
        model="claude-3-opus-20240229",  # Adjust the model if needed
        messages=[
            {"role": "user", "content": messages}
        ],
        max_tokens=4096
    )

    # Extract text from Claude response
    extracted_text += response.content[0].text

    return extracted_text

def main():

    # the three for now, add NOA in future
    doc_types = ["T1", "T4", "FS"]

    names = []
    with open("../test_docs/names.txt", "r") as list_of_files:
        names = list_of_files.read().split() # put names into an array (iterable)
    

    # tqdm to show progress bar
    for name in names:
        for doc_type in doc_types:
            print(f"Starting extraction for {name}'s {doc_type}...")
            file_name = f"{doc_type}{name}.pdf"
            pdf_path = f"../test_docs/test_study_data/{name}/{file_name}"
            
            key_template = ""
            with open(f"../test_docs/templates/{doc_type}Template.txt", "r") as f:
                key_template = f.read()

            image_paths = pdf_to_images(pdf_path, "JPEG")

            extracted_text = claude_extract(image_paths, key_template)

            # indicate which hypothesis it is, in this case it is openai's "CLAUDEHyp"
            save_text_to_file(extracted_text, f"../test_docs/test_study_data/{name}Hyp", f"{doc_type}{name}CLAUDEHyp.txt")

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