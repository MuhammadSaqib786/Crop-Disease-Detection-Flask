# predict.py

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import json
from treatments import disease_info  # Ensure this file contains your readable labels and treatment dict

# ------------------ Load Crop Disease Model ------------------
MODEL_PATH = os.path.join("models", "crop_disease_model.h5")
disease_model = tf.keras.models.load_model(MODEL_PATH)

# ------------------ Load Class Labels ------------------
with open("class_labels.json", "r") as f:
    class_labels = json.load(f)

# ------------------ Load Specialized Leaf Detection Model ------------------
from ultralyticsplus import YOLO

leaf_detector = YOLO("foduucom/plant-leaf-detection-and-classification")

def is_leaf_image(img_path):
    """Use YOLOv8 to check if uploaded image contains a valid crop leaf"""
    results = leaf_detector.predict(img_path, verbose=False)
    
    for result in results:
        #  Check if any bounding box is detected
        if result.boxes is None or result.boxes.data.shape[0] == 0:
            continue

        print(" Valid leaf detected.")
        return True  # At least one box means a plant/leaf is detected

    print(" No leaf detected.")
    return False

# ------------------ Preprocess Image for CNN Model ------------------
def preprocess_image(img_path, target_size=(224, 224)):
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img) / 255.0
    return np.expand_dims(img_array, axis=0)

# ------------------ Main Prediction Function ------------------
def predict_disease(img_path):
    # STEP 1: Pre-Validation for Leaf Detection
    if not is_leaf_image(img_path):
        return "Invalid image. Please upload a crop leaf photo.", 0.0, "No treatment info – not a valid crop image."

    # STEP 2: Crop Disease Prediction
    img = preprocess_image(img_path)
    prediction = disease_model.predict(img)[0]
    predicted_index = np.argmax(prediction)
    predicted_class = class_labels[str(predicted_index)]
    confidence = round(100 * prediction[predicted_index], 2)

    # STEP 3: Friendly Output Mapping
    friendly_name = disease_info.get(predicted_class, {}).get("name", predicted_class)
    treatment = disease_info.get(predicted_class, {}).get("treatment", "Consult your local agriculture expert.")

    return friendly_name, confidence, treatment
