import os
import fitz  # PyMuPDF
from tqdm import tqdm
from PIL import Image
import base64


def pdf_to_images(pdf_path, type_extension, output_folder="temp_images", dpi=300):
    """Convert PDF pages to images using PyMuPDF and save them as JPEG."""
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []
    
    for i, page in tqdm(enumerate(doc)):
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        image_path = os.path.join(output_folder, f"page_{i + 1}.jpg")
        img.save(image_path, type_extension) # save as JPEG or PNG as selected in parameter
        image_paths.append(image_path)
    print("Completed PDF to image conversion.")
    return image_paths


def encode_image(image_path):
    """Encode image as Base64."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def save_text_to_file(output_text, output_file):
    """Save extracted text to a file."""
    if output_file is None:
        output_file = "extracted_text.txt"
    
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

