from tensorflow.keras.utils import img_to_array, load_img # type: ignore
from tensorflow.keras.models import load_model # type: ignore
import numpy as np
import requests
import json
from datetime import datetime
import os

# Load the model
model = load_model('glof_cnn_model.h5')  # Replace with your actual model path
API_KEY = os.getenv('GEMINI_API_KEY')
DATABASE_URL = os.getenv("FIREBASE_DB_URL")
# Preprocess the image
def send_probability_to_firebase_api(probability):
    # Endpoint to send data
    url = f"{DATABASE_URL}/GLOF_Predictions.json?auth={API_KEY}"

    # Data to send
    data = {
        "probability": int(probability),
    }

    # Send data to Firebase
    response = requests.post(url, data=json.dumps(data))
    
    if response.status_code == 200:
        print("Data sent successfully to Firebase.")
    else:
        print(f"Failed to send data. Status code: {response.status_code}, Response: {response.text}")

def preprocess_image(image_path):
    # Load the image in RGB mode and resize it
    image = load_img(image_path, color_mode='rgb', target_size=(128, 128))  # RGB mode
    image_array = img_to_array(image)  # Convert to numpy array
    image_array = image_array / 255.0  # Normalize pixel values
    image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension
    return image_array

# Predict and return the highest probability
def predict_highest_probability(image_path):
    preprocessed_image = preprocess_image(image_path)
    probabilities = model.predict(preprocessed_image)[0]  # Get probabilities
    highest_probability = np.max(probabilities) * 100  # Get highest probability and convert to percentage
    return highest_probability

# Example usage
image_path = 'D:\SAR\preprocessed_2023-06-06-00_00_2023-12-06-23_59_Sentinel-1_IW_VV+VH_IW_-_VH_[dB_gamma0].jpg'  # Replace with your image path
highest_probability = predict_highest_probability(image_path)

# Print the final output
print(f"Probability of glof: {highest_probability:.2f}%")
send_probability_to_firebase_api(highest_probability)