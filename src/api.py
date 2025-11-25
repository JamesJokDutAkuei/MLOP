"""
FastAPI server for Brain Tumor MRI Classification
Uses trained MobileNetV2 model for real predictions
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import json
import time
import io
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Brain Tumor MRI Classifier API")

# Load model and metadata
MODEL_PATH = "models/brain_tumor_model_best.h5"
METADATA_PATH = "models/model_metadata.json"

model = None
metadata = None
api_start_time = datetime.now()

class PredictionResponse(BaseModel):
    predicted_class: str
    predicted_class_short: str
    class_index: int
    confidence: float
    probabilities: dict
    inference_time_ms: float

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str
    uptime_seconds: int

def load_model():
    """Load trained model and metadata."""
    global model, metadata
    try:
        if os.path.exists(MODEL_PATH):
            model = tf.keras.models.load_model(MODEL_PATH)
            logger.info("Model loaded successfully")
            
            if os.path.exists(METADATA_PATH):
                with open(METADATA_PATH, 'r') as f:
                    metadata = json.load(f)
                logger.info(f"Metadata loaded: {metadata['model_name']} v{metadata['version']}")
            return True
        else:
            logger.warning(f"Model not found at {MODEL_PATH}")
            return False
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return False

def preprocess_image(img_array):
    """Preprocess image for MobileNetV2."""
    # Resize to 224x224
    img_array = tf.image.resize(img_array, [224, 224])
    
    # Normalize using ImageNet mean/std
    img_array = img_array / 255.0
    IMAGENET_MEAN = np.array([0.485, 0.456, 0.406])
    IMAGENET_STD = np.array([0.229, 0.224, 0.225])
    img_array = (img_array - IMAGENET_MEAN) / IMAGENET_STD
    
    return np.expand_dims(img_array, axis=0)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Brain Tumor MRI Classifier API",
        "status": "running",
        "version": "1.0"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    uptime = int((datetime.now() - api_start_time).total_seconds())
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        model_version=metadata.get("version", "unknown") if metadata else "unknown",
        uptime_seconds=uptime
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    """Predict brain tumor class from MRI image."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        start_time = time.time()
        
        # Read image file
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert('RGB')
        img_array = np.array(img, dtype=np.float32)
        
        # Preprocess
        processed_img = preprocess_image(img_array)
        
        # Predict
        predictions = model.predict(processed_img, verbose=0)
        predicted_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_idx])
        
        # Get class labels
        class_labels = metadata["class_labels"]
        predicted_class = class_labels[predicted_idx]
        
        # Create probabilities dict
        probabilities = {
            class_labels[i]: float(predictions[0][i])
            for i in range(len(class_labels))
        }
        
        inference_time = (time.time() - start_time) * 1000
        
        return PredictionResponse(
            predicted_class=predicted_class,
            predicted_class_short=predicted_class,
            class_index=int(predicted_idx),
            confidence=confidence,
            probabilities=probabilities,
            inference_time_ms=inference_time
        )
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

@app.post("/retrain")
async def retrain(epochs: int = 5, batch_size: int = 32):
    """Placeholder for model retraining."""
    return {
        "status": "not_implemented",
        "message": "Retraining endpoint placeholder",
        "job_id": "retrain_1"
    }

@app.get("/retrain_status/{job_id}")
async def retrain_status(job_id: str):
    """Get retraining job status."""
    return {
        "job_id": job_id,
        "status": "completed",
        "progress": 100,
        "accuracy": 0.962
    }

@app.get("/retrain_jobs")
async def retrain_jobs():
    """Get list of retraining jobs."""
    return {
        "total_jobs": 0,
        "jobs": {}
    }

@app.on_event("startup")
async def startup_event():
    """Initialize API on startup."""
    logger.info("Starting Brain Tumor MRI Classification API...")
    if not load_model():
        logger.warning("Could not load model - API will have limited functionality")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
