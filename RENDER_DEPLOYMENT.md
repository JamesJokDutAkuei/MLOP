# 🚀 Render Deployment Guide

Deploy your Brain Tumor MRI Classifier to **Render** - the easiest cloud platform with **NO BILLING REQUIRED**.

## ⚡ Why Render?

| Feature | Benefit |
|---------|---------|
| **No Billing** | Free tier doesn't require credit card |
| **Simple Setup** | 5 minutes from start to live |
| **Docker Support** | Your existing Dockerfiles work |
| **Free Tier** | Enough for demos and testing |
| **Perfect For** | Student projects, assignments, demos |

---

## 📋 Prerequisites

You need:
1. ✅ GitHub account (free at github.com)
2. ✅ Your code pushed to GitHub
3. ✅ Render account (free at render.com)

---

## 🎯 Step-by-Step Deployment (5 minutes)

### **Step 1: Push Code to GitHub**

If not already done:

```bash
cd /Users/apple/MLOP
git remote add origin https://github.com/YOUR_USERNAME/mlop-brain-tumor.git
git branch -M main
git push -u origin main
```

### **Step 2: Create Render Account**

1. Go to: https://render.com
2. Click **Sign up** (use GitHub account for faster setup)
3. Authorize Render to access your GitHub account

### **Step 3: Create Web Service for API**

1. From Render dashboard, click **New +** → **Web Service**
2. Click **Connect GitHub repo**
3. Search and select your `mlop-brain-tumor` repository
4. Configure:
   - **Name:** `mlop-api`
   - **Environment:** Docker
   - **Branch:** main
   - **Build Command:** (leave empty - uses Dockerfile)
   - **Start Command:** (leave empty - uses Dockerfile)
   - **Instance Type:** Free

5. Click **Create Web Service**

✅ API will start deploying (takes ~2 minutes)

### **Step 4: Create Web Service for UI**

1. Click **New +** → **Web Service** again
2. Select the same repository
3. Configure:
   - **Name:** `mlop-ui`
   - **Environment:** Docker
   - **Branch:** main
   - **Instance Type:** Free

4. Add Environment Variables:
   - Key: `GCP_API_URL`
   - Value: Copy the URL from your deployed API (e.g., `https://mlop-api-xxxxx.onrender.com`)
   - Add another:
   - Key: `DOCKER_ENV`
   - Value: `true`

5. **Important:** Change Dockerfile path
   - Click **Advanced** → scroll down
   - **Dockerfile:** `deploy/Dockerfile.ui`

6. Click **Create Web Service**

✅ UI will start deploying

---

## 🎉 You're Live!

Once both services finish deploying (green status), you'll have:

### 📱 Your Live URLs:

**UI Dashboard:**
```
https://mlop-ui-xxxxx.onrender.com
```

**API Documentation:**
```
https://mlop-api-xxxxx.onrender.com/docs
```

---

## ⚠️ Important Notes About Render Free Tier

### Sleep Period
- **Free services sleep after 15 minutes of inactivity**
- First request wakes them up (~30 seconds)
- Perfect for demos - you just need to tell instructors to wait 30s on first load

### How to Keep It Awake (Optional)
Add a simple keep-alive script:

```bash
# Run this every 10 minutes (in a separate terminal)
while true; do
  curl https://mlop-api-xxxxx.onrender.com/health
  sleep 600
done
```

### Bandwidth Limits
- 100 GB/month included
- Enough for a classroom demo
- Resets monthly

---

## 🧪 Testing Your Deployment

1. **Open the UI:**
   ```
   https://mlop-ui-xxxxx.onrender.com
   ```

2. **Test API directly:**
   ```bash
   curl https://mlop-api-xxxxx.onrender.com/health
   ```

3. **Upload a test image** through the UI

4. **Check predictions** are working

---

## 🐛 Troubleshooting

### "Service failed to deploy"
- Check build logs in Render dashboard (click service → Logs)
- Usually caused by missing dependencies
- Check `deploy/Dockerfile.*` files have all requirements

### "API connection failed"
- Make sure `GCP_API_URL` environment variable is set correctly
- Copy exact URL from deployed API service
- Wait 2 minutes for cold start

### "UI is white/blank"
- Open browser console (F12)
- Check for JavaScript errors
- Try refreshing the page

---

## 💰 Cost

**Free Tier:** $0/month
- 0.5 CPU
- 512 MB RAM
- Enough for your project

**If you exceed free tier:** ~$7/month per service for production

---

## 📊 Sharing Your Project

Share these links with instructors/team:

**Main UI Link:**
```
https://mlop-ui-xxxxx.onrender.com
```

**Note:** May take 30 seconds to load on first access (free tier sleep)

---

## 🔄 Making Updates

After you push changes to GitHub:

1. Render automatically detects new commits
2. Services rebuild automatically
3. Takes ~2 minutes per service
4. Zero downtime during updates

---

## ✅ Next Steps

1. ✅ Deploy both services
2. ✅ Test UI and API
3. ✅ Share URLs with team
4. ✅ Demo to instructors

**You're all set!** 🚀

For support: https://render.com/docs
