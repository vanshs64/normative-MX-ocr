import os
import io
import json
import base64
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory 
from flask_cors import CORS 
from werkzeug.utils import secure_filename 

import pymupdf
from PIL import Image

from vision import pdf_to_images, google_vision_extract, save_text, cleanup_temp_files
from gpt import openai_extract_responder
from cer import calculate_cer

import json
import os
from pathlib import Path
import io
import base64
HYPOTHESIS_PATH = "../test_docs/hypotheses"
REFERENCE_PATH = "../test_docs/reference"


app = Flask(__name__, static_folder='../frontend/mx-ocr/out', static_url_path='')
CORS(app)

TEST_DOCS_FOLDER = os.path.join(os.path.dirname(os.getcwd()), 'test_docs')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

os.makedirs(TEST_DOCS_FOLDER, exist_ok=True)


def pdf_to_base64_images(pdf_bytes):
    base64_images = []

    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

        base64_images.append({
            "type": "input_image",
            "image_url": f"data:image/jpeg;base64,{encoded}",
            "detail": "high"
        })

    return base64_images


# gpt route for ocr extraction
@app.route('/gptocr', methods=['POST'])
def gptocr():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Please upload PDF, PNG, or JPG files only.'}), 400
    
    filename = secure_filename(file.filename)

    # Read the PDF into bytes

    pdf_bytes = file.read()

    # Convert to images (JPEG format)
    input_images = pdf_to_base64_images(pdf_bytes=pdf_bytes)

    # Determine the document type based on the filename
    if "t1" in filename.lower():
        doc_type = "T1"
    elif "t4" in filename.lower():
        doc_type = "T4"
    elif "fs" in filename.lower():
        doc_type = "FS"
    else:
        return jsonify({'error': 'Unknown document type in filename'}), 400
    
    key_template = ""
    with open(f"../test_docs/templates/{doc_type}Template.txt", "r") as f:
        key_template = f.read()

    print(f"Applying extraction template for {doc_type}")

    extracted_text = openai_extract_responder(input_images, key_template)

    return jsonify(
        {
            'text': extracted_text
        }
    )



@app.route('/get_scanned_files', methods=['GET'])
def get_scanned_files(hypothesis_path=HYPOTHESIS_PATH, reference_path=REFERENCE_PATH):
    
    """Find out which files have an existing reference text to 
    compare the extracted hypothesis text against, 
    and return the list of files names"""

    try:
        hyp_dir = Path(hypothesis_path)
        ref_dir = Path(reference_path)
        
        if not hyp_dir.is_dir() or not ref_dir.is_dir():
            raise ValueError("Invalid directory paths provided")
            
        hyp_files = set(f.name for f in hyp_dir.iterdir() if f.is_file())
        ref_files = set(f.name for f in ref_dir.iterdir() if f.is_file())
        
        # set intersection to find which files exist in both hyp and ref directories
        comparable_files = [''] + list(hyp_files & ref_files)
        #                  ^^^^ adding an empty string at the beginning so that person has to change what the first selected file is in the dropdown
        return comparable_files

    except Exception as e:
        print(f"Error: {str(e)}")
        return []

@app.route('/get_hyp_ref', methods=['POST'])
def get_hyp_ref():
    """Get the contents of the hypothesis and reference files for a given file name."""
    file_name = request.get_json().get('file_name')

    hyp_file_path = Path(HYPOTHESIS_PATH) / file_name
    ref_file_path = Path(REFERENCE_PATH) / file_name

    comparison_table = []
    try:
        with open(hyp_file_path, "r") as hyp_file, open(ref_file_path, "r") as ref_file:
            hyp_content = hyp_file.read()
            hyp_content_dict = json.loads(hyp_content)

            ref_content = ref_file.read()
            ref_content_dict = json.loads(ref_content)

            for key in ref_content_dict.keys():
                comparison_table.append([
                    key, 
                    hyp_content_dict.get(key, "N/A"), 
                    ref_content_dict.get(key, "N/A")
                ])        
            

        # dictionary where "result" is the table and "cer" is the overall cer
        cer_data = calculate_cer(comparison_table)
        print( (cer_data["result"]) )

        return jsonify({"table_data": cer_data["result"], "overall_cer": cer_data["cer"]})

    except Exception as e:
        return jsonify({'error': f'Error processing files: {str(e)}'}), 500

@app.route('/save-file', methods=['POST'])
def save_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Please upload PDF, PNG, or JPG files only.'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(TEST_DOCS_FOLDER, filename)
        
        # Save the file
        file.save(filepath)
        
        if not os.path.exists(filepath):
            return jsonify({'error': f'Failed to save file to {filepath}'}), 500

        # Process the file with vision.py
        try:
            image_paths = pdf_to_images(filepath)
            extracted_text = google_vision_extract(image_paths)
            output_file = f"{os.path.splitext(filepath)[0]}_extracted.txt"
            save_text(extracted_text, output_file)
            cleanup_temp_files(image_paths)
            
            return jsonify({
                'message': 'File processed successfully',
                'filepath': f'test_docs/{filename}',
                'output_file': f'test_docs/{os.path.basename(output_file)}',
                'extracted_text': extracted_text
            })
            
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
