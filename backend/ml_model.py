import numpy as np
import random
from PIL import Image
import logging

logger = logging.getLogger(__name__)

# Simulated ML model (replace with real TensorFlow/PyTorch model)
def predict_crop_health(image_path=None, satellite_data=None, crop_type="paddy", region="Cuttack"):
    """
    Predict crop health using:
    1. Satellite NDVI data
    2. Uploaded image analysis
    3. Historical patterns
    
    In production: Load pre-trained CNN model here
    """
    
    logger.info("Running ML prediction...")
    
    # MOCK PREDICTION (replace with real model inference)
    
    # If satellite data available, use NDVI
    if satellite_data and 'ndvi' in satellite_data:
        ndvi = satellite_data['ndvi']
        # NDVI to health score mapping
        if ndvi > 0.6:
            health_score = random.uniform(75, 90)
            pest_type = "Healthy"
        elif ndvi > 0.4:
            health_score = random.uniform(60, 75)
            pest_type = random.choice(["Brown Spot", "Healthy"])
        else:
            health_score = random.uniform(40, 60)
            pest_type = random.choice(["Brown Spot", "BPH", "Blast"])
    else:
        # Random for demo
        health_score = random.uniform(50, 85)
        pest_type = random.choice(["Healthy", "Brown Spot", "BPH", "Blast"])
    
    # Determine health status
    if health_score >= 70:
        health_status = "Good"
    elif health_score >= 50:
        health_status = "Moderate Risk"
    else:
        health_status = "High Risk"
    
    # Confidence score
    confidence = random.uniform(0.82, 0.95)
    
    result = {
        "health_score": round(health_score, 1),
        "health_status": health_status,
        "pest_type": pest_type,
        "disease_type": pest_type if pest_type != "Healthy" else None,
        "confidence": round(confidence, 2)
    }
    
    logger.info(f"Prediction complete: {result}")
    return result


# PRODUCTION VERSION (uncomment when you have trained model)
"""
import tensorflow as tf

MODEL_PATH = "../models/crop_health_model.h5"
model = tf.keras.models.load_model(MODEL_PATH)

def predict_crop_health_production(image_path):
    img = Image.open(image_path).resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    prediction = model.predict(img_array)
    class_names = ['Healthy', 'Brown Spot', 'BPH', 'Blast']
    
    predicted_class = class_names[np.argmax(prediction)]
    confidence = float(np.max(prediction))
    health_score = (1 - prediction[0][0]) * 100  # Inverse of disease probability
    
    return {
        'health_score': health_score,
        'pest_type': predicted_class,
        'confidence': confidence
    }
"""
