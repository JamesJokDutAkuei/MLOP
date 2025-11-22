# 🚀 GCP Cloud Run Deployment Guide

**Estimated Time:** 10 minutes  
**Cost:** $0 (within free tier for your use case)  
**Difficulty:** ⭐ (Very Easy)

---

## Prerequisites

1. **Google Cloud Account** - Create free account at [console.cloud.google.com](https://console.cloud.google.com)
2. **gcloud CLI** - Install from [cloud.google.com/sdk](https://cloud.google.com/sdk)
3. **Docker** - Already installed ✅

---

## Step 1: Set Up GCP Project

```bash
# Create a new GCP project (or use existing)
gcloud projects create mlop-brain-tumor --name="MLOP Brain Tumor"

# Set as active project
gcloud config set project mlop-brain-tumor

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

---

## Step 2: Configure Docker Authentication

```bash
# Configure Docker to push to Google Container Registry
gcloud auth configure-docker gcr.io

# Verify authentication
docker ps
```

---

## Step 3: Build and Push Docker Image

```bash
# Set project ID
export PROJECT_ID=$(gcloud config get-value project)
export IMAGE_NAME=gcr.io/$PROJECT_ID/mlop-ui:latest

# Build Docker image
docker build -f deploy/Dockerfile.ui -t $IMAGE_NAME .

# Push to Google Container Registry
docker push $IMAGE_NAME

# Push API image
docker build -f deploy/Dockerfile.api -t gcr.io/$PROJECT_ID/mlop-api:latest .
docker push gcr.io/$PROJECT_ID/mlop-api:latest
```

---

## Step 4: Deploy to Cloud Run (UI)

```bash
# Deploy Streamlit UI
gcloud run deploy mlop-ui \
  --image $IMAGE_NAME \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501 \
  --memory 512Mi \
  --timeout 300 \
  --set-env-vars DOCKER_ENV=true
```

**Output will include:**
```
Service URL: https://mlop-ui-xxxxxxxxxx.a.run.app
```

---

## Step 5: Deploy to Cloud Run (API)

```bash
# Deploy API
gcloud run deploy mlop-api \
  --image gcr.io/$PROJECT_ID/mlop-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --timeout 300 \
  --concurrency 80
```

---

## Step 6: Update UI to Use Cloud API

Once API is deployed, update the UI to connect:

Edit `deploy/ui.py` and add:

```python
import os

# In check_api_health() function, update API_URL:
if os.getenv("GCP_API_URL"):
    API_URL = os.getenv("GCP_API_URL")
elif os.getenv("DOCKER_ENV") == "true":
    API_URL = "http://nginx:80"
else:
    API_URL = "http://127.0.0.1:8000"
```

Deploy updated UI:

```bash
docker build -f deploy/Dockerfile.ui -t $IMAGE_NAME .
docker push $IMAGE_NAME

gcloud run deploy mlop-ui \
  --image $IMAGE_NAME \
  --update-env-vars GCP_API_URL=https://mlop-api-xxxxxxxxxx.a.run.app
```

---

## Step 7: Verify Deployment

```bash
# Test API health
curl https://mlop-api-xxxxxxxxxx.a.run.app/health

# Open UI in browser
# https://mlop-ui-xxxxxxxxxx.a.run.app
```

---

## 📊 Monitoring & Logs

```bash
# View Cloud Run logs
gcloud run logs read mlop-ui --limit 50

# View real-time logs
gcloud run logs read mlop-ui --limit 100 --follow

# Check service details
gcloud run services describe mlop-ui
```

---

## 🔧 Troubleshooting

### Port Issues
```bash
# Cloud Run only supports ports 8080, 8081-8083, or user-defined
# UI uses 8501 - ensure Dockerfile exposes it correctly
```

### Memory Issues
```bash
# If service crashes, increase memory
gcloud run deploy mlop-ui \
  --update-env-vars MEMORY=1Gi
```

### Connection Issues
```bash
# If UI can't reach API, check URLs match exactly
# Get exact Cloud Run URLs:
gcloud run services list
```

---

## 💰 Cost Estimate (Free Tier)

| Service | Limit | Your Usage | Cost |
|---------|-------|-----------|------|
| Requests | 2M/month | ~3K/month | $0 |
| Compute | 360K GB-sec/month | ~50K GB-sec/month | $0 |
| Storage | 5GB | ~1GB | $0 |
| **Total** | - | - | **$0** |

---

## 🎉 Deployed!

Your Brain Tumor MRI classifier is now running on Google Cloud Run!

**Share your URLs:**
- 🖥️ UI: `https://mlop-ui-xxxxxxxxxx.a.run.app`
- 🔗 API Docs: `https://mlop-api-xxxxxxxxxx.a.run.app/docs`

---

## Optional: Scale Configuration

```bash
# Adjust concurrency
gcloud run deploy mlop-ui \
  --concurrency 100 \
  --max-instances 100

# View metrics
gcloud monitoring dashboards list
```

---

## Next Steps

1. ✅ Test predictions through the deployed UI
2. ✅ Share URL with others for testing
3. ✅ Set up custom domain (optional)
4. ✅ Configure CI/CD for auto-deployment on push
