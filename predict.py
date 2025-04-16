# predict.py

import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import json
import os
from treatments import disease_info  # Import dictionary from external treatments.py

# Load the trained model
MODEL_PATH = os.path.join("models", "crop_disease_model.h5")
model = tf.keras.models.load_model(MODEL_PATH)

# Load class labels
with open("class_labels.json", "r") as f:
    class_labels = json.load(f)

def preprocess_image(img_path, target_size=(224, 224)):
    """Preprocess image for model prediction"""
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_disease(img_path):
    """Predict the disease from image and return readable result"""
    img = preprocess_image(img_path)
    prediction = model.predict(img)[0]

    predicted_index = np.argmax(prediction)
    predicted_class = class_labels[str(predicted_index)]
    confidence = round(100 * prediction[predicted_index], 2)

    # Get user-friendly name and treatment from dictionary
    friendly_name = disease_info.get(predicted_class, {}).get("name", predicted_class)
    treatment = disease_info.get(predicted_class, {}).get("treatment", "No treatment info available.")

    return friendly_name, confidence, treatment
