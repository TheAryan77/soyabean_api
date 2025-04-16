from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.vgg16 import preprocess_input
from PIL import Image
import numpy as np
import io
import os
import socket
import sys
import gdown
import tensorflow as tf

MODEL_URL = 'https://drive.google.com/file/d/1L51r2z5htdD9z3XSA2DUS987ImtofrnZ/view?usp=drive_link'
MODEL_PATH = 'model_2_new_dataset.h5'

def download_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading model from Google Drive...")
        gdown.download(MODEL_URL, MODEL_PATH, quiet=False, fuzzy=True)

def load_ml_model():
    try:
        # Set input shape configuration
        tf.keras.backend.set_image_data_format('channels_last')
        
        # Custom load function to handle version compatibility
        model = load_model(MODEL_PATH, 
                         compile=False,
                         custom_objects=None,
                         options=tf.saved_model.LoadOptions(
                             experimental_io_device='/job:localhost'
                         ))
        
        print(f"Model loaded successfully from {MODEL_PATH}")
        return model
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        sys.exit(1)  # Exit if model can't be loaded as it's critical

download_model()
model = load_ml_model()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Categories matching the model's output classes
CATEGORIES = ['Healty', 'Yellow Mosaic', 'Sudden Death Syndrome', 'Bacterial Pustule', 'Rust', 'Frogeye Leaf Spot', 'Target Leaf Spot']

def preprocess_image(image_bytes):
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Check if image was successfully loaded
        if image is None:
            raise ValueError("Failed to load image")
            
        # Resize to match model's expected input
        image = image.resize((224, 224))
        # Convert to array and preprocess
        image_array = img_to_array(image)
        image_array = preprocess_input(image_array)
        # Expand dimensions to create batch
        image_array = np.expand_dims(image_array, axis=0)
        return image_array
    except Exception as e:
        raise ValueError(f"Error preprocessing image: {str(e)}")

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except socket.error:
            return True

@app.route('/health', methods=['GET'])
def health_check():
    model_status = "loaded" if model is not None else "not loaded"
    return jsonify({
        'status': 'healthy' if model is not None else 'degraded',
        'message': f'Server is running. Model is {model_status}',
        'model_path': MODEL_PATH
    })

@app.route('/predict', methods=['POST'])
def predict():
    # Check if model is loaded
    if model is None:
        return jsonify({
            'error': 'Model not loaded. Please ensure the model file exists and is valid.'
        }), 503

    # Check if request contains any files
    if not request.files:
        return jsonify({
            'error': 'No files in request'
        }), 400

    # Check for image file specifically
    if 'image' not in request.files:
        return jsonify({
            'error': 'No image field in request. Please use "image" as the field name'
        }), 400

    try:
        image_file = request.files['image']
        
        # Check if a file was actually selected
        if image_file.filename == '':
            return jsonify({
                'error': 'No selected file'
            }), 400

        # Check file extension
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif'}
        file_ext = os.path.splitext(image_file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                'error': f'Invalid file type. Allowed types: {", ".join(allowed_extensions)}'
            }), 400

        # Read and process the image
        image_bytes = image_file.read()
        if not image_bytes:
            return jsonify({
                'error': 'Empty file uploaded'
            }), 400

        processed_image = preprocess_image(image_bytes)
        
        # Get model predictions
        predictions = model.predict(processed_image)
        
        # Get the highest confidence prediction
        predicted_class_index = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_index])
        predicted_class = CATEGORIES[predicted_class_index]
        
        return jsonify({
            'success': True,
            'class': predicted_class,
            'confidence': confidence,
            'predictions': {
                category: float(pred) 
                for category, pred in zip(CATEGORIES, predictions[0])
            }
        })

    except ValueError as ve:
        return jsonify({
            'error': str(ve)
        }), 400
    except Exception as e:
        print(f"Error processing request: {str(e)}")  # Log the error
        return jsonify({
            'error': 'Internal server error while processing image'
        }), 500

@app.route('/test-upload', methods=['POST'])
def test_upload():
    """Test endpoint to debug file uploads"""
    try:
        # Print request information
        print("Content-Type:", request.content_type)
        print("Files:", request.files)
        print("Form:", request.form)
        
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image field in request',
                'files_received': list(request.files.keys()),
                'content_type': request.content_type
            }), 400
            
        image_file = request.files['image']
        return jsonify({
            'success': True,
            'filename': image_file.filename,
            'content_type': image_file.content_type,
            'size': len(image_file.read())
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
