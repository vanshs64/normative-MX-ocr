from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from vision import pdf_to_images, google_vision_extract, save_text, cleanup_temp_files

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
    app.run(host='0.0.0.0', port=1000, debug=True)
