#!/bin/bash

# GCP Cloud Run Deployment Script
# Usage: bash deploy-gcp.sh <project-id> <region>

set -e

PROJECT_ID="${1:-mlop-brain-tumor}"
REGION="${2:-us-central1}"

echo "🚀 Deploying to Google Cloud Platform..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Set project
gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION

# Enable APIs
echo "📋 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Configure Docker
echo "🔐 Configuring Docker..."
gcloud auth configure-docker

# Build images
echo "🔨 Building Docker images..."
docker build -f deploy/Dockerfile.api -t gcr.io/$PROJECT_ID/mlop-api:latest .
docker build -f deploy/Dockerfile.ui -t gcr.io/$PROJECT_ID/mlop-ui:latest .

# Push images
echo "📤 Pushing images to GCR..."
docker push gcr.io/$PROJECT_ID/mlop-api:latest
docker push gcr.io/$PROJECT_ID/mlop-ui:latest

# Deploy API
echo "🚀 Deploying API to Cloud Run..."
gcloud run deploy mlop-api \
  --image gcr.io/$PROJECT_ID/mlop-api:latest \
  --platform managed \
  --region $REGION \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10 \
  --allow-unauthenticated

# Get API URL
API_URL=$(gcloud run services describe mlop-api --platform managed --region $REGION --format 'value(status.url)')
echo "✅ API deployed: $API_URL"

# Deploy UI
echo "🚀 Deploying UI to Cloud Run..."
gcloud run deploy mlop-ui \
  --image gcr.io/$PROJECT_ID/mlop-ui:latest \
  --platform managed \
  --region $REGION \
  --memory 1Gi \
  --cpu 1 \
  --timeout 3600 \
  --max-instances 5 \
  --allow-unauthenticated \
  --set-env-vars "API_URL=$API_URL,DOCKER_ENV=true"

# Get UI URL
UI_URL=$(gcloud run services describe mlop-ui --platform managed --region $REGION --format 'value(status.url)')
echo "✅ UI deployed: $UI_URL"

# Test deployment
echo ""
echo "🧪 Testing deployment..."
sleep 5
curl -s $API_URL/health | python3 -m json.tool || echo "API still starting..."

echo ""
echo "✅ Deployment complete!"
echo "📊 API URL: $API_URL"
echo "🖥️  UI URL: $UI_URL"
echo ""
echo "💡 To view logs:"
echo "   gcloud run services logs read mlop-api"
echo "   gcloud run services logs read mlop-ui"
