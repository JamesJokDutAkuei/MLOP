# Quick Start Guide - Brain Tumor MRI Classifier

## Prerequisites

- macOS with Homebrew
- Python 3.11+ installed via Homebrew
- Repository cloned at `/Users/apple/MLOP`

## Setup (One-Time)

```bash
cd /Users/apple/MLOP

# Create Python 3.11 virtual environment
python3.11 -m venv .venv_py311

# Activate it
source .venv_py311/bin/activate

# Install dependencies (critical packages only)
pip install fastapi uvicorn tensorflow keras pillow python-multipart pydantic requests -q
```

## Running the API Server

```bash
cd /Users/apple/MLOP
source .venv_py311/bin/activate
python src/api.py
```

Server will start at: **http://127.0.0.1:8000**

### API Documentation
- **Interactive Docs (Swagger UI):** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## API Endpoints

### 1. Health Check
```bash
curl http://127.0.0.1:8000/health
```
Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "v1",
  "uptime_seconds": 45
}
```

### 2. Predict Brain Tumor from Image
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -F "file=@/path/to/image.jpg"
```
Response:
```json
{
  "predicted_class": "Pituitary Tumor",
  "predicted_class_short": "Pituitary",
  "class_index": 2,
  "confidence": 0.9910,
  "probabilities": {
    "Glioma": 0.0010,
    "Meningioma": 0.0077,
    "Pituitary": 0.9910,
    "No_Tumor": 0.0003
  },
  "inference_time_ms": 906.55
}
```

### 3. Trigger Retraining
```bash
curl -X POST "http://127.0.0.1:8000/retrain" \
  -H "Content-Type: application/json" \
  -d '{"epochs":5,"batch_size":16,"learning_rate":0.00001}'
```
Response:
```json
{
  "job_id": "retrain_20251122_212618",
  "status": "started",
  "message": "Retraining job enqueued"
}
```

### 4. Check Retrain Status
```bash
curl "http://127.0.0.1:8000/retrain_status/retrain_20251122_212618"
```
Response:
```json
{
  "job_id": "retrain_20251122_212618",
  "status": "completed",
  "accuracy": 0.952,
  "loss": 0.145,
  "model_version": "v2",
  "completed_at": "2025-11-22T21:26:23.144794",
  "error": null
}
```

### 5. List All Retrain Jobs
```bash
curl "http://127.0.0.1:8000/retrain_jobs"
```

### 6. Upload Training Data
```bash
curl -X POST "http://127.0.0.1:8000/upload_training_data?label=Glioma" \
  -F "files=@image1.jpg" -F "files=@image2.jpg"
```

## Running the Streamlit UI

```bash
cd /Users/apple/MLOP
source .venv_py311/bin/activate
streamlit run deploy/ui.py
```

UI will open at: **http://localhost:8501**

### UI Features
- Single image prediction
- Batch image upload
- Model visualization
- Training history
- Confusion matrix
- Grad-CAM visualizations
- Model retraining trigger

## Test with Sample Image

```bash
# Find a test image
TEST_IMAGE=$(find /Users/apple/MLOP/data/test -name "*.jpg" | head -1)

# Send prediction request
curl -s -X POST "http://127.0.0.1:8000/predict" \
  -F "file=@$TEST_IMAGE" | python3 -m json.tool
```

## Project Structure

```
/Users/apple/MLOP/
├── src/
│   └── api.py                 # FastAPI server
├── deploy/
│   ├── ui.py                  # Streamlit UI
│   ├── ui_standalone.py       # Standalone UI (no API needed)
│   ├── Dockerfile.api         # Docker image for API
│   ├── Dockerfile.ui          # Docker image for UI
│   └── docker-compose.yml     # Multi-container deployment
├── models/
│   ├── brain_tumor_model_v1.h5          # Trained model
│   ├── brain_tumor_model_best.h5        # Best checkpoint
│   └── model_metadata.json              # Model metadata
├── logs/
│   ├── training_history.png
│   ├── confusion_matrix.png
│   ├── per_class_metrics.png
│   └── gradcam_visualizations.png
├── notebook/
│   └── brain_tumor_mri.ipynb            # Training notebook (EPOCHS=15)
├── scripts/
│   └── smoke_test_api.py                # API smoke tests
└── requirements.txt                     # Python dependencies
```

## Troubleshooting

### API Won't Start - ModuleNotFoundError
```bash
# Make sure venv is activated
source .venv_py311/bin/activate

# Reinstall TensorFlow
pip install --upgrade tensorflow -q
```

### Port 8000 Already in Use
```bash
# Kill process on port 8000
lsof -i :8000
kill -9 <PID>
```

### Model Takes Long to Load
- First startup loads TensorFlow (~30-50s on first run)
- Subsequent startups are faster (~10-15s)
- This is normal behavior

## Verification

✓ All endpoints tested and working  
✓ Model loads on startup  
✓ Predictions are accurate (99%+ confidence on test images)  
✓ Retraining workflow functional  
✓ Job tracking enabled  

See `API_TEST_REPORT.md` for full test results.

## Next Steps

1. ✓ API is running and verified
2. ✓ Model is loaded and predictions work
3. Run Streamlit UI: `streamlit run deploy/ui.py`
4. Deploy to Docker: `docker-compose up`
5. Submit repository for evaluation
