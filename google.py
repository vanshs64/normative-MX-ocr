import os
import sys
import json
import base64

from pdf2image import convert_from_path
from google.cloud import vision
from PIL import Image



def extract_images_from_pdf(pdf_path, output_folder, dpi=300):
    images = convert_from_path(pdf_path, dpi=dpi)
    image_paths = []
    
    for i, image in enumerate(images):
        img_path = os.path.join(output_folder, f'page_{i + 1}.png')
        image.save(img_path, 'PNG')
        image_paths.append(img_path)
    
    return image_paths

def resize_image(image_path, target_height):
    with Image.open(image_path) as img:
        width, height = img.size
        new_width = int((target_height / height) * width)
        resized_img = img.resize((new_width, target_height), Image.LANCZOS)
        resized_img.save(image_path)

def process_image_with_vision_api(image_path):
    client = vision.ImageAnnotatorClient()
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    
    extracted_text = response.full_text_annotation.text
    
    illustrations = []
    if response.label_annotations:
        illustrations = [label.description for label in response.label_annotations]
    
    return {
        "text": extracted_text,
        "illustrations": illustrations
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <pdf_filename>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_folder = "processed_images"
    os.makedirs(output_folder, exist_ok=True)
    
    print("Extracting images from PDF...")
    image_paths = extract_images_from_pdf(pdf_path, output_folder)
    
    print("Processing images...")
    extracted_data = {}
    
    for i, image_path in enumerate(image_paths):
        # Determine resizing factor based on quality (low or high)
        resize_height = 3500 if i == 0 else 2000  # First page might be low quality
        resize_image(image_path, resize_height)
        
        print(f"Processing page {i+1}...")
        extracted_data[f"page_{i+1}"] = process_image_with_vision_api(image_path)
    
    json_output = pdf_path.replace(".pdf", ".json")
    with open(json_output, "w", encoding="utf-8") as json_file:
        json.dump(extracted_data, json_file, indent=4, ensure_ascii=False)
    
    print(f"Processing complete. JSON saved as {json_output}")
    
if __name__ == "__main__":
    main()
