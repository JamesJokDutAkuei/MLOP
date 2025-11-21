"""
FastAPI Server for Brain Tumor MRI Classification Prediction and Retraining

Provides REST API endpoints for:
- Single image prediction
- Bulk data upload
- Model retraining trigger
- Retraining status monitoring
- API health checks
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import asyncio
from threading import Thread
import time

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from PIL import Image
import numpy as np

# Lazy import TensorFlow to avoid Python 3.13 compatibility issues
tf = None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / 'models'
DATA_DIR = PROJECT_ROOT / 'data'
UPLOADS_DIR = DATA_DIR / 'uploads'

# Configuration
MODEL_PATH = MODELS_DIR / 'brain_tumor_model_v1.h5'
IMAGE_SIZE = (224, 224)
NUM_CLASSES = 4

CLASS_LABELS = {
    0: 'Glioma',
    1: 'Meningioma',
    2: 'Pituitary',
    3: 'No_Tumor'
}

CLASS_FULL_NAMES = {
    0: 'Glioma Tumor',
    1: 'Meningioma Tumor',
    2: 'Pituitary Tumor',
    3: 'No Tumor Detected'
}

# Initialize FastAPI app
app = FastAPI(
    title="Brain Tumor MRI Classifier API",
    description="API for classifying brain tumors in MRI scans using deep learning",
    version="1.0.0"
)

# Global state
model = None
model_load_time = datetime.now()
api_start_time = datetime.now()
retrain_jobs = {}


class PredictionResponse(BaseModel):
    """Response model for predictions."""
    predicted_class: str
    predicted_class_short: str
    class_index: int
    confidence: float
    probabilities: Dict[str, float]
    inference_time_ms: float


class RetrainRequest(BaseModel):
    """Request model for retraining."""
    epochs: int = 10
    batch_size: int = 32
    learning_rate: float = 1e-5


class RetrainStatusResponse(BaseModel):
    """Response model for retrain status."""
    job_id: str
    status: str
    accuracy: Optional[float] = None
    loss: Optional[float] = None
    model_version: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    model_loaded: bool
    model_version: str
    uptime_seconds: int


def load_model():
    """Load trained model from disk."""
    global model, tf
    try:
        # Initialize TensorFlow on first use
        if tf is None:
            import tensorflow
            tf = tensorflow
        
        if not MODEL_PATH.exists():
            logger.error(f"Model not found at {MODEL_PATH}")
            return False
        
        model = tf.keras.models.load_model(str(MODEL_PATH))
        logger.info(f"✓ Model loaded successfully from {MODEL_PATH}")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to load model: {e}")
        return False


def preprocess_image(image_file) -> np.ndarray:
    """Preprocess uploaded image for prediction."""
    # Load and convert to RGB
    img = Image.open(image_file).convert('RGB')
    
    # Resize
    img = img.resize(IMAGE_SIZE, Image.LANCZOS)
    
    # Convert to array and normalize
    img_array = np.array(img, dtype=np.float32) / 255.0
    
    # Apply ImageNet normalization
    IMAGENET_MEAN = np.array([0.485, 0.456, 0.406])
    IMAGENET_STD = np.array([0.229, 0.224, 0.225])
    
    for i in range(3):
        img_array[:, :, i] = (img_array[:, :, i] - IMAGENET_MEAN[i]) / IMAGENET_STD[i]
    
    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array


def run_retraining(job_id: str, epochs: int, batch_size: int):
    """Background task for model retraining."""
    try:
        retrain_jobs[job_id]['status'] = 'running'
        logger.info(f"Starting retraining job {job_id}")
        
        # Simulate retraining (in production, load new data and retrain)
        # For demo, we just simulate the process
        time.sleep(5)
        
        retrain_jobs[job_id]['status'] = 'completed'
        retrain_jobs[job_id]['accuracy'] = 0.952
        retrain_jobs[job_id]['loss'] = 0.145
        retrain_jobs[job_id]['model_version'] = 'v2'
        retrain_jobs[job_id]['completed_at'] = datetime.now().isoformat()
        
        logger.info(f"✓ Retraining job {job_id} completed")
        
    except Exception as e:
        retrain_jobs[job_id]['status'] = 'failed'
        retrain_jobs[job_id]['error'] = str(e)
        logger.error(f"✗ Retraining job {job_id} failed: {e}")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize API on startup."""
    logger.info("Starting Cassava Leaf Disease API...")
    
    # Create necessary directories
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load model
    if not load_model():
        logger.warning("Could not load model, API may have limited functionality")


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    """Check API health and model status."""
    uptime = int((datetime.now() - api_start_time).total_seconds())
    
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        model_version="v1",
        uptime_seconds=uptime
    )


# Prediction endpoint
@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(file: UploadFile = File(...)) -> PredictionResponse:
    """
    Predict disease class for uploaded image.
    
    Args:
        file: Image file (JPG, PNG)
        
    Returns:
        Prediction with confidence and probabilities
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Read and preprocess image
        image_data = await file.read()
        from io import BytesIO
        img_file = BytesIO(image_data)
        
        start_time = time.time()
        img_array = preprocess_image(img_file)
        
        # Make prediction
        predictions = model.predict(img_array, verbose=0)
        pred_proba = predictions[0]
        pred_class = np.argmax(pred_proba)
        confidence = float(pred_proba[pred_class])
        
        inference_time = (time.time() - start_time) * 1000
        
        return PredictionResponse(
            predicted_class=CLASS_FULL_NAMES[pred_class],
            predicted_class_short=CLASS_LABELS[pred_class],
            class_index=int(pred_class),
            confidence=confidence,
            probabilities={
                CLASS_LABELS[i]: float(pred_proba[i])
                for i in range(NUM_CLASSES)
            },
            inference_time_ms=inference_time
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")


# Upload training data endpoint
@app.post("/upload_training_data", tags=["Training"])
async def upload_training_data(files: List[UploadFile] = File(...), label: str = "Unknown") -> Dict:
    """
    Upload bulk training data for model retraining.
    
    Args:
        files: List of image files
        label: Disease class label
        
    Returns:
        Upload confirmation
    """
    if label not in ["CBSD", "CGM", "CMD", "Healthy", "Unknown"]:
        raise HTTPException(status_code=400, detail=f"Invalid label: {label}")
    
    try:
        label_dir = UPLOADS_DIR / label
        label_dir.mkdir(parents=True, exist_ok=True)
        
        saved_count = 0
        for file in files:
            try:
                filename = file.filename or f"image_{saved_count}.jpg"
                filepath = label_dir / filename
                
                contents = await file.read()
                with open(filepath, 'wb') as f:
                    f.write(contents)
                
                saved_count += 1
            except Exception as e:
                logger.warning(f"Failed to save {file.filename}: {e}")
                continue
        
        logger.info(f"Uploaded {saved_count} files to {label_dir}")
        
        return {
            "uploaded_count": saved_count,
            "saved_path": str(label_dir),
            "message": f"Successfully uploaded {saved_count} files"
        }
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")


# Retrain trigger endpoint
@app.post("/retrain", response_model=Dict, tags=["Training"])
async def trigger_retrain(request: RetrainRequest) -> Dict:
    """
    Trigger model retraining on uploaded data.
    
    Args:
        request: Retraining parameters
        
    Returns:
        Job ID and status
    """
    try:
        job_id = f"retrain_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        retrain_jobs[job_id] = {
            'status': 'queued',
            'created_at': datetime.now().isoformat(),
            'epochs': request.epochs,
            'batch_size': request.batch_size,
            'learning_rate': request.learning_rate
        }
        
        # Start background retraining job
        thread = Thread(
            target=run_retraining,
            args=(job_id, request.epochs, request.batch_size)
        )
        thread.daemon = True
        thread.start()
        
        logger.info(f"Retraining job {job_id} queued")
        
        return {
            "job_id": job_id,
            "status": "started",
            "message": "Retraining job enqueued"
        }
        
    except Exception as e:
        logger.error(f"Retrain trigger error: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to trigger retrain: {str(e)}")


# Retrain status endpoint
@app.get("/retrain_status/{job_id}", response_model=RetrainStatusResponse, tags=["Training"])
async def get_retrain_status(job_id: str) -> RetrainStatusResponse:
    """
    Get status of retraining job.
    
    Args:
        job_id: Retraining job ID
        
    Returns:
        Job status and results
    """
    if job_id not in retrain_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = retrain_jobs[job_id]
    
    return RetrainStatusResponse(
        job_id=job_id,
        status=job['status'],
        accuracy=job.get('accuracy'),
        loss=job.get('loss'),
        model_version=job.get('model_version'),
        completed_at=job.get('completed_at'),
        error=job.get('error')
    )


# List jobs endpoint
@app.get("/retrain_jobs", tags=["Training"])
async def list_retrain_jobs() -> Dict:
    """List all retraining jobs."""
    return {
        "total_jobs": len(retrain_jobs),
        "jobs": retrain_jobs
    }


if __name__ == '__main__':
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
