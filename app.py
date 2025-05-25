from flask import Flask, request, jsonify
import pytesseract
from PIL import Image, ImageEnhance
import re
import io
import os
import requests
from flask_cors import CORS
import platform

app = Flask(__name__)

CORS(app)
# Configure Tesseract path (keep your existing configuration)
# Only set tesseract path on Windows
if platform.system() == 'Windows':
    pytesseract.pytesseract.tesseract_cmd = r'c:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image):
    try:
        # Pre-processing for clearer images (resize, convert to grayscale, and enhance contrast)
        image = image.resize((image.width * 2, image.height * 2))
        image = image.convert("L")
        # image = ImageEnhance.Contrast(image).enhance(0.1) 
        
        extracted_text = pytesseract.image_to_string(image, lang='eng', config='--psm 6')
        
        # cleaned_text = re.sub(r'[^\w\s\n]', '', extracted_text)
        
        return extracted_text.strip()
    
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    # Check if the request contains a file
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    
    # Check if the file is empty
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    try:
        # Open the image directly from the file stream
        image = Image.open(io.BytesIO(file.read()))
        extracted_text = extract_text_from_image(image)
        
        if extracted_text:
            return jsonify({'text': extracted_text})
        else:
            return jsonify({'error': 'Text extraction failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HF_API_KEY = os.getenv("HF_API_KEY", "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")  # Default key as fallback

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        # Get text from request body
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Text is required"}), 400

        text = data['text']

        # Call Hugging Face API
        headers = {
            "Authorization": f"Bearer {HF_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {"inputs": text}
        
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json=payload
        )

        # Handle errors from Hugging Face API
        if not response.ok:
            error_data = response.json()
            error_msg = error_data.get('error', response.reason)
            raise Exception(error_msg)

        # Extract summary from response
        result = response.json()
        summary = result[0].get('summary_text', 'No summary generated')

        return jsonify({"summary": summary})

    except Exception as e:
        print(f"Summarization Error: {str(e)}")
        return jsonify({
            "error": "Failed to summarize text",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
