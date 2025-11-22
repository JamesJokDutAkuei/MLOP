# ✅ GCP Cloud Run - Easy Step-by-Step Guide

> **No command line needed!** You can do everything from the GCP Console

---

## Step 1: Create GCP Account (Free)

1. Go to https://console.cloud.google.com
2. Click "Get Started" if you don't have an account
3. Sign up with your Google account (free $300 credit!)
4. Accept terms

---

## Step 2: Create a Project

1. At the top, click "Select a project" dropdown
2. Click "New Project"
3. Enter name: `mlop-brain-tumor`
4. Click "Create"
5. Wait ~1 minute for project to be created
6. Select your new project from dropdown

---

## Step 3: Enable APIs

1. Search for "API Library" in the search bar
2. Search for "Cloud Run API" → Click → Click "Enable"
3. Search for "Container Registry API" → Click → Click "Enable"
4. Go back (you should see them listed)

---

## Step 4: Upload Docker Images

### Option A: Using Cloud Console (Easiest)

1. Go to "Cloud Build" → "Builds"
2. Click "Create"
3. Connect your GitHub repo (if you have one) or:
4. Use "Cloud Code" to build locally

### Option B: Using Terminal Commands

```bash
# Install gcloud using Docker (no local install needed):
docker run --rm -it \
  -v ~/.config/gcloud:/root/.config/gcloud \
  -v /Users/apple/MLOP:/workspace \
  google/cloud-sdk:latest \
  /bin/bash

# Inside container:
cd /workspace
gcloud auth login  # Opens browser for login
gcloud config set project mlop-brain-tumor

# Build and push images
export PROJECT_ID=mlop-brain-tumor

docker build -f deploy/Dockerfile.api \
  -t gcr.io/$PROJECT_ID/mlop-api:latest .

docker push gcr.io/$PROJECT_ID/mlop-api:latest

# Do same for UI...
```

---

## Step 5: Deploy API to Cloud Run

1. Go to "Cloud Run" → Click "Create Service"
2. Choose "Deploy one revision from an existing container image"
3. Click "Select" to choose image
4. Paste image name: `gcr.io/mlop-brain-tumor/mlop-api:latest`
5. Service name: `mlop-api`
6. Region: `us-central1`
7. Allow unauthenticated invocations: ✅ Check
8. Click "Deploy"
9. Wait ~2-3 minutes
10. Copy the service URL when it appears

---

## Step 6: Deploy UI to Cloud Run

1. Go to "Cloud Run" → Click "Create Service"
2. Choose container image: `gcr.io/mlop-brain-tumor/mlop-ui:latest`
3. Service name: `mlop-ui`
4. Region: `us-central1`
5. Allow unauthenticated: ✅ Check
6. Click "Set environment variables"
7. Add:
   - `GCP_API_URL` = (paste the API URL from Step 5)
   - `DOCKER_ENV` = `false`
8. Click "Deploy"
9. Wait ~2-3 minutes

---

## Step 7: Test Your Deployment

1. Click on `mlop-ui` service
2. Copy the URL
3. Open in browser: `https://mlop-ui-xxxxx.a.run.app`
4. Try uploading an MRI image
5. Verify prediction works

---

## 🎉 Success!

Your app is now live on Google Cloud!

**Your URLs:**
- UI: `https://mlop-ui-xxxxx.a.run.app`
- API: `https://mlop-api-xxxxx.a.run.app`
- API Docs: `https://mlop-api-xxxxx.a.run.app/docs`

**Cost:** $0/month (within free tier)

---

## 📋 Cheat Sheet

| Task | Where |
|------|-------|
| View logs | Cloud Run → Service → Logs |
| Monitor usage | Cloud Run → Service → Metrics |
| Stop service | Cloud Run → Delete service |
| Scale up | Cloud Run → Service → Edit & Deploy |
| Set domain | Cloud Run → Service → Manage Custom Domains |

---

## ❓ Troubleshooting

### "Service failed to deploy"
- Check logs: Cloud Run → Service → Logs
- Common issue: Port not exposed in Dockerfile
- Solution: Ensure `EXPOSE 8501` (UI) and `EXPOSE 8000` (API)

### "UI says API not available"
- Check API URL environment variable
- Must match exactly, including https://

### "Image not found"
- Check image name is correct
- Ensure you pushed to Container Registry
- Wait 1-2 minutes for image to be available

---

## 💡 Pro Tips

1. **Keep monitoring costs** - though you shouldn't exceed free tier
2. **Set up alerts** - Go to "Billing" → "Budgets"
3. **Use cloud shell** - Built-in terminal in GCP Console
4. **Export logs** - For debugging and analysis

---

**Next:** Share your URL with others to test! 🚀
