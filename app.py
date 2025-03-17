from flask import Flask, request, render_template, jsonify
import os
from werkzeug.utils import secure_filename
from claude import extract_images_from_pdf, resize_image, process_image_with_claude_ocr
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist with absolute paths
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(os.getcwd(), 'processed_images'), exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        try:
            # Create directories if they don't exist
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the file
            file.save(filepath)
            
            if not os.path.exists(filepath):
                return jsonify({'error': f'Failed to save file to {filepath}'}), 500
            
            output_folder = os.path.join(os.getcwd(), "processed_images")
            os.makedirs(output_folder, exist_ok=True)
            
            api_key = os.getenv("ANTHROPIC_API_KEY")
            
            if not api_key:
                return jsonify({'error': "ANTHROPIC_API_KEY not found in environment variables"}), 500
            
            if filepath.lower().endswith('.pdf'):
                image_paths = extract_images_from_pdf(filepath, output_folder)
            else:
                image_paths = [filepath]
            
            extracted_data = {}
            for i, image_path in enumerate(image_paths):
                resize_height = 3500 if i == 0 else 2000
                resize_image(image_path, resize_height)
                extracted_data[f"page_{i+1}"] = process_image_with_claude_ocr(image_path, api_key)
            
            # Clean up
            try:
                os.remove(filepath)
                for path in image_paths:
                    if os.path.exists(path):
                        os.remove(path)
            except Exception as e:
                print(f"Cleanup error: {str(e)}")
            
            return jsonify(extracted_data)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Change host and port as needed
    # host='0.0.0.0' makes it accessible from other devices on the network
    # You can use any port number above 1024 (e.g., 8080, 3000, etc.)
    app.run(host='0.0.0.0', port=8080, debug=True)
