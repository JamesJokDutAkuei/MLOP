"""
Brain Tumor MRI Classifier API - Mock Version
Uses file-based predictions matching trained model classes
No TensorFlow required for Render deployment
"""
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time
from io import BytesIO
from PIL import Image
import numpy as np
import os
from pathlib import Path

app = FastAPI(title="Brain Tumor MRI Classifier API")

# Allow cross-origin requests (useful if a browser calls the API directly)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

APP_VERSION = "mock-1.1.0"

@app.get("/")
async def root():
    return {"message": "Brain Tumor MRI Classifier API", "status": "running", "version": APP_VERSION}

class PredictionResponse(BaseModel):
    predicted_class: str
    predicted_class_short: str
    class_index: int
    confidence: float
    probabilities: dict
    inference_time_ms: float

class UploadResponse(BaseModel):
    uploaded_count: int
    saved_path: str
    message: str

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": True,
        "model_version": "v1",
        "uptime_seconds": 100
    }

# ----------------------------------------------------------------------------
# In-memory metrics
# ----------------------------------------------------------------------------
REQUEST_COUNT = 0
TOTAL_INFERENCE_MS = 0.0
LAST_LATENCIES: List[float] = []
CLASS_COUNTS = {"Glioma": 0, "Meningioma": 0, "Pituitary": 0, "No_Tumor": 0}

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

    result = PredictionResponse(
        predicted_class=f"{classes[predicted_idx]} Tumor" if predicted_idx != 3 else "No_Tumor",
        predicted_class_short=class_short[predicted_idx],
        class_index=predicted_idx,
        confidence=max(probs.values()),
        probabilities=probs,
        inference_time_ms=inference_time
    )

    # update metrics
    global REQUEST_COUNT, TOTAL_INFERENCE_MS, LAST_LATENCIES, CLASS_COUNTS
    REQUEST_COUNT += 1
    TOTAL_INFERENCE_MS += inference_time
    LAST_LATENCIES.append(inference_time)
    if len(LAST_LATENCIES) > 5:
        LAST_LATENCIES = LAST_LATENCIES[-5:]
    CLASS_COUNTS[result.predicted_class_short] = CLASS_COUNTS.get(result.predicted_class_short, 0) + 1

    return result

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

@app.get("/metrics")
async def metrics():
    avg_latency = (TOTAL_INFERENCE_MS / REQUEST_COUNT) if REQUEST_COUNT > 0 else 0.0
    return {
        "request_count": REQUEST_COUNT,
        "avg_inference_ms": avg_latency,
        "last_5_latencies_ms": LAST_LATENCIES,
        "class_counts": CLASS_COUNTS,
    }

@app.post("/upload_training_data", response_model=UploadResponse)
async def upload_training_data(label: str, files: List[UploadFile] = File(...)):
    """Accept multiple images and store under data/uploads/{label}/"""
    base_dir = Path("data/uploads") / label
    base_dir.mkdir(parents=True, exist_ok=True)
    saved = 0
    for f in files:
        try:
            content = await f.read()
            # ensure filename
            name = f.filename or f"upload_{int(time.time()*1000)}.jpg"
            out_path = base_dir / name
            with open(out_path, "wb") as out:
                out.write(content)
            saved += 1
        except Exception:
            continue
    return UploadResponse(
        uploaded_count=saved,
        saved_path=str(base_dir),
        message="Files uploaded successfully" if saved > 0 else "No files saved"
    )

@app.get("/dataset_stats")
async def dataset_stats():
    """Return basic dataset statistics for visualizations."""
    stats_path = Path("data/dataset_stats.json")
    if stats_path.exists():
        import json
        with open(stats_path, "r") as f:
            return json.load(f)
    # Fallback minimal stats
    return {
        "class_distribution": {
            "Glioma": 1000,
            "Meningioma": 1000,
            "Pituitary": 1000,
            "No_Tumor": 1000
        },
        "avg_brightness_by_class": {
            "Glioma": 0.42,
            "Meningioma": 0.45,
            "Pituitary": 0.47,
            "No_Tumor": 0.51
        },
        "avg_resolution": {
            "width": 224,
            "height": 224
        }
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
