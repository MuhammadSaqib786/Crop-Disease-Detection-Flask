# predict.py

import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import json
import os

# Load the trained model
MODEL_PATH = os.path.join("models", "crop_disease_model.h5")
model = tf.keras.models.load_model(MODEL_PATH)

# Load class labels
with open("class_labels.json", "r") as f:
    class_labels = json.load(f)

# Optional: You can create a treatment mapping
treatments = {
    "Tomato___Early_blight": "Use fungicides containing chlorothalonil or mancozeb.",
    "Apple___Black_rot": "Remove infected leaves and apply copper-based fungicides.",
    "Grape___Esca_(Black_Measles)": "Prune affected parts and improve drainage.",
    # Add more if needed...
}

def preprocess_image(img_path, target_size=(224, 224)):
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_disease(img_path):
    img = preprocess_image(img_path)
    prediction = model.predict(img)[0]
    predicted_index = np.argmax(prediction)
    predicted_class = class_labels[str(predicted_index)]
    confidence = round(100 * prediction[predicted_index], 2)

    # Get treatment suggestion
    treatment = treatments.get(predicted_class, "Consult your local agriculture extension office for treatment.")

    return predicted_class, confidence, treatment
