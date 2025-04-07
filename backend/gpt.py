import os
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv
import time

import ast

from helpers import pdf_to_images, encode_image, save_text_to_file

from calculate_score import append_score_to_csv
import json

# Load API key from .env file
load_dotenv()
OPENAI_SECRET_KEY = os.getenv("OPENAI_SECRET_KEY")

def openai_extract(image_paths, key_template):
    """Send images to OpenAI Vision API for OCR text extraction."""
    client = OpenAI(api_key=OPENAI_SECRET_KEY)

    reference_text = key_template

    extracted_text = ""
    
    print("Beginning OCR text extraction via API...")
    for image_path in tqdm(image_paths):
        base64_image = encode_image(image_path)
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "user", "content": [
                    {f"type": "input_text", 
                     "text": "Extract all text from this image. Please expect to find the mapping between key-value pairs given through these extracted data dictionary keys: {reference_text}. Please return a value pair for each of these in a similar dictionary format. If a reference is already found to that "},
                    {"type": "input_image", 
                     "image_url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}
                ]}
            ]
        )
        extracted_text += response.output_text + "\n\n"
        time.sleep(1)  # wait for 1 second between requests to avoid quota exceeding
    
    return extracted_text

def main():

    # the three for now, add NOA in future
    doc_types = ["T1", "T4", "FS"]

    names = []
    with open("../test_docs/names.txt", "r") as list_of_files:
        names = list_of_files.read().split() # put names into an array (iterable)
    

    # tqdm to show progress bar
    for name in tqdm(names):
        for doc_type in tqdm(doc_types):
            print(f"Starting extraction for {name}'s {doc_type}...")
            file_name = f"{doc_type}{name}.pdf"
            pdf_path = f"../test_docs/test_study_data/{name}/{file_name}"
            
            key_template_path = f"../test_docs/templates/{doc_type}Template.txt"
            key_template = ""
            with open(key_template_path, "r") as f:
                key_template = f.read()

            image_paths = pdf_to_images(pdf_path, "JPEG")


            extracted_text = openai_extract(image_paths, key_template)

            # indicate which hypothesis it is, in this case it is openai's "GPTHyp"
            save_text_to_file(extracted_text, f"../test_docs/test_study_data/{name}Hyp", f"{doc_type}{name}GPTHyp.txt")

            print(f"Extraction for {name}'s {doc_type} done.")
        
        print(f"OCR completed for {file_name}. Extracted text saved to {doc_type}{file_name}Hyp.txt")

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
