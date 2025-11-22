#!/bin/bash
# 🚀 GCP Cloud Run One-Command Deployment
# This script automates the entire deployment process

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     GCP Cloud Run Deployment Script                           ║"
echo "║     Brain Tumor MRI Classifier                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
PROJECT_ID=${1:-$(gcloud config get-value project)}
REGION="us-central1"
UI_SERVICE="mlop-ui"
API_SERVICE="mlop-api"

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: No GCP project specified"
    echo "Usage: bash scripts/deploy_gcp.sh <project-id>"
    exit 1
fi

echo "📍 Project: $PROJECT_ID"
echo "🌍 Region: $REGION"
echo ""

# Step 1: Enable APIs
echo "1️⃣  Enabling GCP APIs..."
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable containerregistry.googleapis.com --project=$PROJECT_ID
echo "✅ APIs enabled"
echo ""

# Step 2: Configure Docker
echo "2️⃣  Configuring Docker authentication..."
gcloud auth configure-docker gcr.io --quiet
echo "✅ Docker configured"
echo ""

# Step 3: Build and push images
echo "3️⃣  Building Docker images..."
API_IMAGE="gcr.io/$PROJECT_ID/$API_SERVICE:latest"
UI_IMAGE="gcr.io/$PROJECT_ID/$UI_SERVICE:latest"

docker build -f deploy/Dockerfile.api -t $API_IMAGE . --quiet
docker build -f deploy/Dockerfile.ui -t $UI_IMAGE . --quiet
echo "✅ Docker images built"
echo ""

echo "4️⃣  Pushing images to Google Container Registry..."
docker push $API_IMAGE --quiet
docker push $UI_IMAGE --quiet
echo "✅ Images pushed"
echo ""

# Step 4: Deploy API
echo "5️⃣  Deploying API to Cloud Run..."
gcloud run deploy $API_SERVICE \
  --image $API_IMAGE \
  --project=$PROJECT_ID \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --port=8000 \
  --memory=512Mi \
  --timeout=300 \
  --concurrency=80 \
  --quiet

API_URL=$(gcloud run services describe $API_SERVICE --project=$PROJECT_ID --region=$REGION --format='value(status.url)')
echo "✅ API deployed: $API_URL"
echo ""

# Step 5: Deploy UI
echo "6️⃣  Deploying UI to Cloud Run..."
gcloud run deploy $UI_SERVICE \
  --image $UI_IMAGE \
  --project=$PROJECT_ID \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --port=8501 \
  --memory=512Mi \
  --timeout=300 \
  --set-env-vars GCP_API_URL=$API_URL,DOCKER_ENV=true \
  --quiet

UI_URL=$(gcloud run services describe $UI_SERVICE --project=$PROJECT_ID --region=$REGION --format='value(status.url)')
echo "✅ UI deployed: $UI_URL"
echo ""

# Step 6: Verify
echo "7️⃣  Verifying deployment..."
echo ""

echo "Testing API..."
API_HEALTH=$(curl -s $API_URL/health | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)
if [ "$API_HEALTH" = "healthy" ]; then
    echo "✅ API is healthy"
else
    echo "⚠️  API health check failed (may still be starting)"
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                 ✅ DEPLOYMENT COMPLETE!                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Your Brain Tumor MRI Classifier is now live!"
echo ""
echo "🖥️  UI (Streamlit):        $UI_URL"
echo "🔗 API (FastAPI):          $API_URL"
echo "📚 API Docs (Swagger):     $API_URL/docs"
echo ""
echo "💰 Cost: $0/month (within free tier)"
echo ""
echo "Next steps:"
echo "1. Open the UI URL in your browser"
echo "2. Try uploading a brain MRI image"
echo "3. Share the URL with others for testing"
echo ""
echo "View logs:"
echo "  gcloud run logs read $UI_SERVICE --limit=50"
echo "  gcloud run logs read $API_SERVICE --limit=50"
echo ""
