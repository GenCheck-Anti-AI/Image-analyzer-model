from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
from PIL import Image  
import numpy as np

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Dummy function to simulate AI detection
def is_ai_generated(image: Image.Image):
    # Convert image to array and calculate dummy score
    img_array = np.array(image.resize((64, 64))).astype(np.float32) / 255.0
    fake_score = np.mean(img_array)  # Mock scoring
    is_fake = fake_score > 0.5
    return {
        "prediction": "AI-generated" if is_fake else "Human",
        "probability": round(float(fake_score if is_fake else 1 - fake_score), 4)
    }

# Check valid image
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Main route
@app.route('/analyze/image', methods=['POST'])
def analyze_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
        file.save(filepath)

        try:
            image = Image.open(filepath)
            result = is_ai_generated(image)
            os.remove(filepath)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': f'Failed to process image: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/')
def home():
    return jsonify({'message': 'Image Analyzer is up'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
