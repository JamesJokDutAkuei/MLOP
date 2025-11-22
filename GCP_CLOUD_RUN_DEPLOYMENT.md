# 🚀 GCP Cloud Run Deployment Guide

**Estimated Time:** 15 minutes  
**Cost:** $0 (within free tier for your use case)  
**Difficulty:** ⭐ (Very Easy)

---

## Prerequisites Checklist

- [ ] Google Cloud Account (free account at [console.cloud.google.com](https://console.cloud.google.com))
- [ ] Project created in GCP Console
- [ ] Docker installed ✅
- [ ] gcloud CLI installed (or use Docker)
- [ ] Your project files ready ✅

---

## 🎯 Quick Start (Fastest Option)

### Option A: Using Docker with gcloud (Recommended)

```bash
# Run deployment in Docker container (no local gcloud needed)
docker run --rm -it \
  -v ~/.config/gcloud:/root/.config/gcloud \
  -v /Users/apple/MLOP:/workspace \
  google/cloud-sdk:latest \
  bash

# Inside container:
cd /workspace

# Initialize gcloud
gcloud init

# Then follow the steps below
```

### Option B: Install gcloud Locally

```bash
# For macOS, use: https://cloud.google.com/sdk/docs/install-sdk
# Manual download and install

# Or fix Python issue:
export CLOUDSDK_PYTHON=python3.11
# Then retry: brew install --cask google-cloud-sdk
```

---

## Step-by-Step Deployment

### 1️⃣ Set Up GCP Project

Go to [console.cloud.google.com](https://console.cloud.google.com) and:

1. Click "Select a project" at the top
2. Click "New Project"
3. Enter name: `mlop-brain-tumor`
4. Click "Create"
5. Wait for project to be created
6. Select your new project

Or via CLI:

```bash
gcloud projects create mlop-brain-tumor --name="MLOP Brain Tumor"
gcloud config set project mlop-brain-tumor
```

---

### 2️⃣ Enable Required APIs

In GCP Console or via CLI:

```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable compute.googleapis.com
```

---

### 3️⃣ Set Up Docker Authentication

```bash
# Configure Docker to push to GCP Container Registry
gcloud auth configure-docker gcr.io
```

---

### 4️⃣ Build and Push Docker Images

```bash
# Set your GCP project ID
export PROJECT_ID=$(gcloud config get-value project)

echo "🔨 Building API image..."
docker build -f deploy/Dockerfile.api \
  -t gcr.io/$PROJECT_ID/mlop-api:latest .

echo "🔨 Building UI image..."
docker build -f deploy/Dockerfile.ui \
  -t gcr.io/$PROJECT_ID/mlop-ui:latest .

echo "📤 Pushing API image..."
docker push gcr.io/$PROJECT_ID/mlop-api:latest

echo "📤 Pushing UI image..."
docker push gcr.io/$PROJECT_ID/mlop-ui:latest

echo "✅ Images pushed successfully!"
```

---

### 5️⃣ Deploy API to Cloud Run

```bash
export PROJECT_ID=$(gcloud config get-value project)

gcloud run deploy mlop-api \
  --image gcr.io/$PROJECT_ID/mlop-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --timeout 300 \
  --concurrency 80

# Save the API URL (you'll need it next)
export API_URL=$(gcloud run services describe mlop-api \
  --region us-central1 \
  --format='value(status.url)')

echo "API deployed at: $API_URL"
```

---

### 6️⃣ Update UI with API URL

Edit `deploy/ui.py` and update the API configuration:

Find this section at the top of the file:

```python
# API Configuration - Auto-detect environment
if os.getenv("DOCKER_ENV") == "true":
    API_URL = "http://nginx:80"  # Docker internal network
else:
    API_URL = "http://127.0.0.1:8000"
```

Replace with:

```python
# API Configuration - Auto-detect environment
if os.getenv("GCP_API_URL"):
    API_URL = os.getenv("GCP_API_URL")  # GCP Cloud Run
elif os.getenv("DOCKER_ENV") == "true":
    API_URL = "http://nginx:80"  # Docker internal network
else:
    API_URL = "http://127.0.0.1:8000"  # Local development
```

---

### 7️⃣ Deploy UI to Cloud Run

```bash
export PROJECT_ID=$(gcloud config get-value project)
export API_URL=$(gcloud run services describe mlop-api \
  --region us-central1 \
  --format='value(status.url)')

# Rebuild UI image with updated code
docker build -f deploy/Dockerfile.ui \
  -t gcr.io/$PROJECT_ID/mlop-ui:latest .

# Push new image
docker push gcr.io/$PROJECT_ID/mlop-ui:latest

# Deploy UI with API URL
gcloud run deploy mlop-ui \
  --image gcr.io/$PROJECT_ID/mlop-ui:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501 \
  --memory 512Mi \
  --timeout 300 \
  --set-env-vars GCP_API_URL=$API_URL,DOCKER_ENV=false

echo "✅ UI deployed!"
```

---

### 8️⃣ Get Your URLs

```bash
export PROJECT_ID=$(gcloud config get-value project)

echo "📊 Your deployment URLs:"
echo ""
echo "🖥️  UI (Streamlit):"
gcloud run services describe mlop-ui --region us-central1 \
  --format='value(status.url)'

echo ""
echo "🔗 API (FastAPI):"
gcloud run services describe mlop-api --region us-central1 \
  --format='value(status.url)'

echo ""
echo "📚 API Docs (Swagger):"
gcloud run services describe mlop-api --region us-central1 \
  --format='value(status.url)' | sed 's/$//g' && echo "/docs"
```

---

### 9️⃣ Test Your Deployment

```bash
# Get API URL
API_URL=$(gcloud run services describe mlop-api --region us-central1 --format='value(status.url)')

# Test API health
curl -s $API_URL/health | python3 -m json.tool

# Get UI URL and open in browser
UI_URL=$(gcloud run services describe mlop-ui --region us-central1 --format='value(status.url)')
echo "Open this URL in your browser: $UI_URL"
```

---

## 📊 Monitor Your Deployment

```bash
# View API logs
gcloud run logs read mlop-api --region us-central1 --limit 50

# View UI logs
gcloud run logs read mlop-ui --region us-central1 --limit 50

# View real-time logs
gcloud run logs read mlop-api --region us-central1 --follow

# Check service metrics
gcloud run services describe mlop-api --region us-central1
```

---

## 💰 Cost Estimate (Free Tier)

| Resource | Limit | Your Usage | Cost |
|----------|-------|-----------|------|
| **Requests/month** | 2,000,000 | ~3,000 | $0 |
| **Compute (GB-sec)** | 360,000 | ~50,000 | $0 |
| **Storage** | 5GB | ~1GB | $0 |
| **Network** | 1GB outbound | <100MB | $0 |
| **Total Monthly** | - | - | **$0** |

✅ Your usage is well within free tier limits!

---

## 🔧 Common Issues & Fixes

### Issue: "API Not Available" in UI

**Solution:** Check that API URL environment variable is set:

```bash
gcloud run services describe mlop-ui --region us-central1 --format=json | grep GCP_API_URL
```

### Issue: Container Takes Too Long to Start

**Solution:** Increase memory or timeout:

```bash
gcloud run deploy mlop-ui \
  --memory 1Gi \
  --timeout 600
```

### Issue: "Service account has insufficient permissions"

**Solution:** Grant permissions:

```bash
gcloud run deploy mlop-ui \
  --set-cloudsql-instances=PROJECT_ID:REGION:INSTANCE
```

### Issue: "Port is not supported"

**Solution:** Cloud Run supports specific ports. Ensure:
- UI uses 8501 ✅
- API uses 8000 ✅
- Both are in Dockerfile ✅

---

## 🎉 Success! Your App is Live

Once deployed, you'll have:

- 🖥️ **Streamlit UI** at: `https://mlop-ui-xxxxx.a.run.app`
- 🔗 **FastAPI Backend** at: `https://mlop-api-xxxxx.a.run.app`
- 📚 **API Documentation** at: `https://mlop-api-xxxxx.a.run.app/docs`

---

## 📋 Next Steps

1. ✅ Test uploading an MRI image
2. ✅ Verify predictions are working
3. ✅ Share URLs with others
4. ✅ Monitor usage in Cloud Console
5. ✅ Set up custom domain (optional)

---

## 🚀 Advanced Features

### Auto-Deploy on Git Push (Optional)

```bash
# Set up Cloud Build for auto-deployment
gcloud builds submit --region=us-central1 \
  --config=cloudbuild.yaml
```

### Set Custom Domain (Optional)

1. Go to Cloud Run service
2. Click "Manage Custom Domains"
3. Map your domain

### Scale Configuration

```bash
# Increase max concurrent requests
gcloud run deploy mlop-ui --concurrency 100 --max-instances 100
```

---

## 📞 Need Help?

- GCP Console: https://console.cloud.google.com
- Cloud Run Docs: https://cloud.google.com/run/docs
- Troubleshooting: https://cloud.google.com/run/docs/troubleshooting
