# 🚀 RENDER QUICK START (5 MINUTES)

## The Absolute Simplest Path

### **1. GitHub** (2 min)
```bash
cd /Users/apple/MLOP
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/mlop.git
git branch -M main
git push -u origin main
```

### **2. Render Account**
- Go to: https://render.com
- Sign up with GitHub
- Skip billing setup (not required for free tier)

### **3. Deploy API**
1. Dashboard → **New +** → **Web Service**
2. Connect your GitHub repo
3. Name: `mlop-api`
4. Environment: **Docker**
5. Instance Type: **Free**
6. Click **Create**

✅ Done! API deploying...

### **4. Deploy UI**
1. **New +** → **Web Service**
2. Same repo
3. Name: `mlop-ui`
4. Environment: **Docker**
5. Instance Type: **Free**
6. **Advanced** → Dockerfile: `deploy/Dockerfile.ui`
7. **Environment:**
   - Add: `DOCKER_ENV` = `true`
   - Add: `GCP_API_URL` = `https://mlop-api-XXXXX.onrender.com` (copy from API service)
8. Click **Create**

✅ Done! Both services deploying...

---

## 🎉 You're Live!

**Wait 3-5 minutes for both to turn green.**

Then access:
- **UI:** `https://mlop-ui-XXXXX.onrender.com`
- **API:** `https://mlop-api-XXXXX.onrender.com/docs`

---

## ⚠️ Just Remember

- First request takes 30 seconds (cold start)
- Auto-sleep after 15 minutes of inactivity
- Free tier = plenty for demos

---

## 📚 Full Guide

See `RENDER_DEPLOYMENT.md` for detailed instructions and troubleshooting.
