# 🚀 Deploy to GCP Cloud Run (EASIEST)

## Quick Start (~5 minutes)

### Prerequisites
```bash
# Install Google Cloud SDK
brew install google-cloud-sdk

# Login to GCP
gcloud auth login

# Set project
gcloud config set project YOUR-PROJECT-ID
```

### Deploy API
```bash
# Build and push to GCP
gcloud run deploy mlop-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DOCKER_ENV=true \
  --memory 2Gi \
  --timeout 3600

# Output will show: https://mlop-api-xxxxx.run.app
```

### Deploy UI (Streamlit)
```bash
gcloud run deploy mlop-ui \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DOCKER_ENV=true \
  --memory 2Gi \
  --timeout 3600
```

### Update UI to point to cloud API
Edit `deploy/ui.py` and change:
```python
if os.getenv("DOCKER_ENV") == "true":
    # Cloud Run (external)
    api_url = "https://mlop-api-xxxxx.run.app"
else:
    api_url = "http://127.0.0.1:8000"
```

## What You Get
✅ **Auto-scaling** - Handles traffic spikes automatically  
✅ **Pay-per-request** - Only pay when requests come in  
✅ **Managed service** - No infrastructure to maintain  
✅ **Instant deploy** - Changes live in seconds  
✅ **Free tier** - 2M requests/month free  

## Monitoring
```bash
# View logs
gcloud run logs read mlop-api --limit=50

# View metrics
gcloud monitoring dashboards create --config-from-file=dashboard.json

# Scale settings
gcloud run services update mlop-api \
  --min-instances 0 \
  --max-instances 100
```

## Cleanup
```bash
gcloud run services delete mlop-api
gcloud run services delete mlop-ui
```

---

**That's it! Your app is now running on GCP!** 🎉
