# 🌐 Deploy to Render via Dashboard (Browser)

Since the CLI approach has authentication issues, here's the **fastest browser-based deployment** (still just 5 minutes):

## 📋 What You Need

✅ Your GitHub account (already has code pushed)
✅ Render account with API key (you have it!)
✅ Your API key: `SEH5-JUG1-3T3M-FPL7`

---

## 🎯 One-Time Dashboard Setup (5 minutes)

### **Step 1: Go to Render Dashboard**

https://dashboard.render.com

Sign in with your account

### **Step 2: Create API Service**

1. Click **New +** → **Web Service**
2. Select: **Deploy an existing repository**
3. Find and click: **JamesJokDutAkuei/MLOP**
4. Fill in:
   - **Name:** `mlop-api`
   - **Branch:** `main`
   - **Runtime:** Docker
   - **Build Command:** (leave empty)
   - **Start Command:** (leave empty)
   - **Dockerfile Path:** `deploy/Dockerfile.api`
5. Environment Variables:
   - `PORT` = `8000`
   - `PYTHON_UNBUFFERED` = `1`
6. **Instance Type:** Free
7. Click **Create Web Service**

✅ API will start building (~2 min)

### **Step 3: Get API URL**

Once API finishes building, you'll see:
```
https://mlop-api-xxxxx.onrender.com
```

Copy this URL.

### **Step 4: Create UI Service**

1. Click **New +** → **Web Service**
2. Select: **Deploy an existing repository**
3. Find and click: **JamesJokDutAkuei/MLOP**
4. Fill in:
   - **Name:** `mlop-ui`
   - **Branch:** `main`
   - **Runtime:** Docker
   - **Build Command:** (leave empty)
   - **Start Command:** (leave empty)
   - **Dockerfile Path:** `deploy/Dockerfile.ui`
5. Environment Variables:
   - `PORT` = `8501`
   - `GCP_API_URL` = `https://mlop-api-xxxxx.onrender.com` (paste from Step 3)
   - `DOCKER_ENV` = `true`
   - `STREAMLIT_SERVER_HEADLESS` = `true`
6. **Instance Type:** Free
7. Click **Create Web Service**

✅ UI will start building (~2 min)

---

## 🎉 You're Live!

Once both services turn **green**, access:

```
🎨 UI:   https://mlop-ui-xxxxx.onrender.com
📚 API:  https://mlop-api-xxxxx.onrender.com/docs
```

---

## ⏱️ Timeline

- Services show as "Building" → 2-3 minutes
- Turn green when ready ✅
- First load may take 30 seconds (cold start)

---

## 📊 View Your Services

At any time, go to: https://dashboard.render.com

You'll see both services listed with their URLs.

---

## 🔄 Auto-Redeploy on Updates

After deployment, whenever you push to GitHub:

```bash
git push origin main
```

Render automatically rebuilds! ✅

---

## ✅ Done!

Share the UI URL with your instructors:
```
https://mlop-ui-xxxxx.onrender.com
```

**That's it!** Your app is live on the internet. 🚀
