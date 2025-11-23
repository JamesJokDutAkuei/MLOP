# 📤 Push to GitHub (Required for Render Deployment)

Render requires your code to be on GitHub. Follow these steps:

## **Step 1: Create GitHub Repository**

1. Go to: https://github.com/new
2. Repository name: `mlop-brain-tumor` (or any name you prefer)
3. Description: "Brain Tumor MRI Classification with ML, API, and Streamlit UI"
4. Select **Public** (so Render can access it)
5. Click **Create repository**

---

## **Step 2: Push Your Code**

Copy these commands and run in your terminal:

```bash
cd /Users/apple/MLOP

# Initialize git (if not already done)
git init

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/mlop-brain-tumor.git

# Rename branch to main
git branch -M main

# Add all files
git add .

# First commit
git commit -m "🚀 Brain Tumor MRI Classifier - Initial deployment setup"

# Push to GitHub
git push -u origin main
```

---

## **Step 3: Verify on GitHub**

1. Go to: `https://github.com/YOUR_USERNAME/mlop-brain-tumor`
2. You should see all your files
3. This is the repository URL you'll use in Render

---

## **Step 4: Render Deployment**

Now follow: `RENDER_QUICK_START.md`

---

## ✅ Done!

Your code is now on GitHub and ready for Render deployment! 🎉
