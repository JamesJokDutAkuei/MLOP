# 🚀 Heroku Deployment (Simplest Free Option)

**Time:** 5 minutes  
**Cost:** $0 (free tier)  
**Difficulty:** ⭐ (Easiest)

---

## Quick Start

### 1. Install Heroku CLI

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Verify
heroku --version
```

### 2. Login to Heroku

```bash
heroku login
```

This opens a browser to authenticate.

### 3. Create Heroku App

```bash
# Create app
heroku create mlop-brain-tumor

# Or use custom name
heroku create my-custom-name
```

### 4. Deploy with Git

```bash
# Add Heroku remote
heroku git:remote -a mlop-brain-tumor

# Push to deploy
git push heroku main

# Done! 🎉
```

---

## That's it!

Your app is now live at: `https://mlop-brain-tumor.herokuapp.com`

---

## View Logs

```bash
heroku logs --tail
```

---

## Scale the App

```bash
# Use 1 free dyno (sleeps after 30 min inactivity)
heroku ps:scale web=1

# View dyno hours remaining
heroku account:limits
```

---

## Environment Variables

```bash
# Set API URL
heroku config:set DOCKER_ENV=true

# View all config
heroku config
```

---

## 💰 Heroku Free Tier

| Resource | Limit | Cost |
|----------|-------|------|
| Dyno Hours | 550/month | $0 |
| Database | 10,000 rows | $0 |
| Data Transfer | 1GB/month | $0 |

**Limitation:** App sleeps after 30 minutes of inactivity

---

## Quick Comparison

| Feature | Heroku | GCP Cloud Run |
|---------|--------|---------------|
| Setup Time | 5 min | 10 min |
| Easiness | ⭐⭐⭐ | ⭐⭐ |
| Cold Start | ~5 sec | ~1 sec |
| Always On | ❌ Sleeps | ✅ Always |
| Free Tier | $0 (with limits) | $0 (generous) |
| **Best For** | Quick demos | Production |

---

## If You Need Always-On

Upgrade to Heroku Paid ($7/month for reliable dyno):

```bash
# Scale to paid dyno
heroku dyno:type standard-1x

# Cost: $7/month
```

---

**Try Heroku first if you want the simplest setup!** 🚀
