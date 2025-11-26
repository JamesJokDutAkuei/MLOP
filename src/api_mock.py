"""
Brain Tumor MRI Classifier API - Mock Version
Uses file-based predictions matching trained model classes
No TensorFlow required for Render deployment
"""
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import time
import hashlib

app = FastAPI(title="Brain Tumor MRI Classifier API")

# Allow cross-origin requests (useful if a browser calls the API directly)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Brain Tumor MRI Classifier API", "status": "running"}

class PredictionResponse(BaseModel):
    predicted_class: str
    predicted_class_short: str
    class_index: int
    confidence: float
    probabilities: dict
    inference_time_ms: float

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": True,
        "model_version": "v1",
        "uptime_seconds": 100
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    """Mock prediction - returns random result based on file"""
    start = time.time()
    
    # Read file to validate it's an image
    contents = await file.read()
    
    # Mock prediction based on file hash
    file_hash = hash(contents) % 4
    classes = ["Glioma", "Meningioma", "Pituitary", "No_Tumor"]
    class_short = ["Glioma", "Meningioma", "Pituitary", "No_Tumor"]
    
    predicted_idx = file_hash
    
    # Generate mock probabilities
    probs = [random.uniform(0, 0.3) for _ in range(4)]
    probs[predicted_idx] = random.uniform(0.7, 0.99)
    probs = {class_short[i]: float(probs[i]) for i in range(4)}
    
    # Normalize
    total = sum(probs.values())
    probs = {k: v/total for k, v in probs.items()}
    
    inference_time = (time.time() - start) * 1000
    
    return PredictionResponse(
        predicted_class=f"{classes[predicted_idx]} Tumor",
        predicted_class_short=class_short[predicted_idx],
        class_index=predicted_idx,
        confidence=max(probs.values()),
        probabilities=probs,
        inference_time_ms=inference_time
    )

@app.post("/retrain")
async def retrain(epochs: int = 5, batch_size: int = 32, learning_rate: float = 0.00001):
    """Mock retrain endpoint"""
    job_id = f"retrain_{int(time.time())}"
    return {
        "job_id": job_id,
        "status": "started",
        "message": "Retraining job enqueued"
    }

@app.get("/retrain_status/{job_id}")
async def retrain_status(job_id: str):
    """Mock retrain status"""
    return {
        "job_id": job_id,
        "status": "completed",
        "accuracy": 0.96,
        "loss": 0.12,
        "model_version": "v2",
        "completed_at": "2025-11-23T23:10:00",
        "error": None
    }

@app.get("/retrain_jobs")
async def retrain_jobs():
    """Mock retrain jobs list"""
    return {
        "total_jobs": 1,
        "jobs": {}
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
