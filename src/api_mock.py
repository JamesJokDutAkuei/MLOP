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
from io import BytesIO
from PIL import Image
import numpy as np

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
    # Load image safely
    try:
        img = Image.open(BytesIO(contents)).convert("L")  # grayscale
    except Exception:
        # Fallback to previous random behavior if image cannot be parsed
        file_hash = hash(contents) % 4
        classes = ["Glioma", "Meningioma", "Pituitary", "No_Tumor"]
        class_short = ["Glioma", "Meningioma", "Pituitary", "No_Tumor"]
        probs = [0.1, 0.1, 0.1, 0.1]
        probs[file_hash] = 0.7
        total = sum(probs)
        probs = {class_short[i]: float(probs[i]/total) for i in range(4)}
        inference_time = (time.time() - start) * 1000
        return PredictionResponse(
            predicted_class=f"{classes[file_hash]} Tumor",
            predicted_class_short=class_short[file_hash],
            class_index=file_hash,
            confidence=max(probs.values()),
            probabilities=probs,
            inference_time_ms=inference_time
        )

    # Resize to standard size for consistent stats
    img = img.resize((256, 256))
    arr = np.asarray(img, dtype=np.float32) / 255.0

    # Basic stats
    mean_intensity = float(arr.mean())
    var_intensity = float(arr.var())

    # Edge density via gradient magnitudes
    gx = np.abs(arr[:, 1:] - arr[:, :-1])
    gy = np.abs(arr[1:, :] - arr[:-1, :])
    grad_mag = np.pad(gx, ((0,0),(0,1))) + np.pad(gy, ((0,1),(0,0)))
    edge_density = float((grad_mag > 0.08).mean())  # threshold tuned lightly

    # Feature-driven class mapping (deterministic)
    # Heuristic rationale (very rough):
    # - Higher edge density & variance -> likely tumor structures
    # - Lower variance & smoother textures -> No_Tumor
    # - Medium variance with moderate edges -> Pituitary/Meningioma buckets
    classes = ["Glioma", "Meningioma", "Pituitary", "No_Tumor"]
    class_short = ["Glioma", "Meningioma", "Pituitary", "No_Tumor"]

    if edge_density > 0.18 and var_intensity > 0.035:
        predicted_idx = 0  # Glioma
    elif edge_density > 0.14 and var_intensity > 0.025:
        predicted_idx = 1  # Meningioma
    elif var_intensity > 0.02 and mean_intensity > 0.45:
        predicted_idx = 2  # Pituitary
    else:
        predicted_idx = 3  # No_Tumor

    # Construct probabilities with softmax-like shaping around selected class
    base = np.array([0.15, 0.15, 0.15, 0.15], dtype=np.float32)
    # Increase confidence based on feature strength
    strength = float(0.6 + 0.4 * np.clip(edge_density*2 + var_intensity*5, 0, 1))
    base[predicted_idx] = strength
    probs = base / base.sum()
    probs = {class_short[i]: float(probs[i]) for i in range(4)}

    inference_time = (time.time() - start) * 1000

    return PredictionResponse(
        predicted_class=f"{classes[predicted_idx]} Tumor" if predicted_idx != 3 else "No_Tumor",
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
