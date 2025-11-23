# 🚀 Render CLI Deployment Guide

Deploy to Render using **command-line interface (CLI)** - no browser clicks needed!

## ⚡ Why CLI?

✅ **Faster** - Single command does everything
✅ **Reproducible** - Can automate in scripts  
✅ **Scriptable** - Use in CI/CD pipelines
✅ **Same Result** - Identical to browser deployment

---

## 📋 Prerequisites

### 1. GitHub Account & Repository
Make sure your code is on GitHub:

```bash
cd /Users/apple/MLOP
git remote add origin https://github.com/YOUR_USERNAME/mlop.git
git push -u origin main
```

### 2. Render Account
Create free account at: https://render.com (use GitHub to sign up)

---

## 🎯 One-Command Deployment

### **Method 1: Auto-Install Render CLI (Recommended)**

```bash
bash /Users/apple/MLOP/deploy-render-cli.sh
```

This script will:
1. ✅ Install Render CLI (if needed)
2. ✅ Authenticate with Render
3. ✅ Push code to GitHub
4. ✅ Deploy API service
5. ✅ Deploy UI service
6. ✅ Give you live URLs

---

## 🛠️ Manual CLI Steps (If Script Doesn't Work)

### **Step 1: Install Render CLI**

**macOS:**
```bash
brew tap render-oss/render
brew install render
```

**Linux:**
```bash
curl -fsSL https://render.com/install.sh | sh
```

**Verify:**
```bash
render --version
```

### **Step 2: Authenticate**
```bash
render auth login
```

Browser opens → Approve access → Done

### **Step 3: Deploy API**
```bash
render deploy \
  --name mlop-api \
  --type web \
  --repo https://github.com/YOUR_USERNAME/mlop.git \
  --region us-west \
  --instance-type free \
  --dockerfile deploy/Dockerfile.api \
  --env PORT=8000 \
  --env PYTHON_UNBUFFERED=1
```

### **Step 4: Get API URL**
```bash
render services describe mlop-api --format json | jq '.url'
```

Copy the URL (you'll need it for UI)

### **Step 5: Deploy UI**
```bash
render deploy \
  --name mlop-ui \
  --type web \
  --repo https://github.com/YOUR_USERNAME/mlop.git \
  --region us-west \
  --instance-type free \
  --dockerfile deploy/Dockerfile.ui \
  --env PORT=8501 \
  --env GCP_API_URL=https://YOUR_API_URL.onrender.com \
  --env DOCKER_ENV=true \
  --env STREAMLIT_SERVER_HEADLESS=true
```

### **Step 6: Get UI URL**
```bash
render services describe mlop-ui --format json | jq '.url'
```

---

## 📊 Useful Render CLI Commands

### **View All Services**
```bash
render services
```

### **View Service Details**
```bash
render services describe mlop-api
render services describe mlop-ui
```

### **View Logs**
```bash
render logs mlop-api
render logs mlop-ui
```

### **Update Service**
```bash
render deploy --name mlop-api --repo YOUR_REPO_URL
```

### **Delete Service**
```bash
render services delete mlop-api
```

### **Get API Key (for scripts)**
```bash
render auth token
```

---

## 🔑 Environment Variables Reference

| Variable | Value | Purpose |
|----------|-------|---------|
| `PORT` | `8000` (API), `8501` (UI) | Listen port |
| `GCP_API_URL` | API service URL | UI connects to API |
| `DOCKER_ENV` | `true` | Enable Docker-specific settings |
| `STREAMLIT_SERVER_HEADLESS` | `true` | Disable Streamlit GUI (server mode) |
| `PYTHON_UNBUFFERED` | `1` | Real-time Python output |

---

## 📈 Monitoring

### **Real-time Logs**
```bash
render logs mlop-api -f
render logs mlop-ui -f
```

### **Service Status**
```bash
render services describe mlop-api
```

### **Check Health**
```bash
curl https://mlop-api-xxxxx.onrender.com/health
```

---

## 🐛 Troubleshooting

### "render: command not found"
```bash
# Install Render CLI
brew tap render-oss/render
brew install render
```

### "Authentication failed"
```bash
render auth login
```

### "Deploy failed - see logs"
```bash
render logs mlop-api
```

Check for missing dependencies or environment variable issues.

### "Services still deploying"
- Takes 2-3 minutes for first deploy
- UI auto-updates API URL once API is ready
- Patience! ⏳

---

## ✅ Verify Deployment

Once both services are running:

```bash
# Check API
curl https://mlop-api-xxxxx.onrender.com/health

# Check UI (should return HTML)
curl -I https://mlop-ui-xxxxx.onrender.com
```

---

## 🔄 Auto-Redeploy on Push

Render automatically redeploys when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "Update model"
git push origin main

# Render auto-rebuilds! ✅
```

---

## 💰 Cost

**Free Tier (CLI same as Browser):**
- ✅ $0/month for demo
- ✅ 0.5 CPU
- ✅ 512 MB RAM
- ✅ Auto-sleep after 15 min inactivity

---

## 🎯 Full Workflow

```bash
# 1. Setup
cd /Users/apple/MLOP
git remote add origin https://github.com/YOUR_USERNAME/mlop.git
git push -u origin main

# 2. Deploy (one command!)
bash deploy-render-cli.sh

# 3. Wait for services to start (~2-3 min)
render services

# 4. Test
curl https://mlop-api-xxxxx.onrender.com/health

# 5. Share URLs with team!
```

---

## 📚 Resources

- **Render CLI Docs:** https://render.com/docs/cli
- **Render API Docs:** https://render.com/docs/api
- **GitHub Integration:** https://render.com/docs/github

---

**Ready?** Run:
```bash
bash /Users/apple/MLOP/deploy-render-cli.sh
```

🚀
