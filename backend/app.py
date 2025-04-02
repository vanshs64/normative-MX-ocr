from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from vision import pdf_to_images, google_vision_extract, save_text, cleanup_temp_files

import json
import os
from pathlib import Path
HYPOTHESIS_PATH = "../test_docs/hypotheses"
REFERENCE_PATH = "../test_docs/reference"


app = Flask(__name__, static_folder='../frontend/mx-ocr/out', static_url_path='')
CORS(app)

TEST_DOCS_FOLDER = os.path.join(os.path.dirname(os.getcwd()), 'test_docs')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

os.makedirs(TEST_DOCS_FOLDER, exist_ok=True)

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/gpt', methods=['POST'])
def extract_text():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        
        # Process the text with Google Vision API (or any other processing)
        # For now, we just return the text back
        return jsonify({'extracted_text': text})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
    try:
        file_name = request.get_json().get('file_name')
        if not file_name:
            return jsonify({'error': 'Missing file_name parameter'}), 400

        hyp_file_path = Path(HYPOTHESIS_PATH) / file_name
        ref_file_path = Path(REFERENCE_PATH) / file_name

        # Verify files exist before opening
        if not hyp_file_path.exists() or not ref_file_path.exists():
            return jsonify({'error': 'One or both files not found'}), 404

        with open(hyp_file_path, 'r') as hyp_file, open(ref_file_path, 'r') as ref_file:
            return jsonify({
                'hyp_content': json.load(hyp_file),
                'ref_content': json.load(ref_file)
            })

    except json.JSONDecodeError as e:
        return jsonify({'error': f'Invalid JSON format in files: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Error processing files: {str(e)}'}), 500
    
print(get_scanned_files())

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
