# Brain Tumor MRI Dataset Setup Guide

## ✅ Correct Dataset Link

**Brain Tumor MRI Classification Dataset**  
🔗 https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset

**Dataset Info:**
- 4 classes: Glioma, Meningioma, Pituitary, No_Tumor
- ~7,400 MRI brain scan images
- 512×512 px grayscale images (.jpg format)
- ~300-400 MB total size

---

## 📥 How to Download the Data

### Option 1: Using kagglehub (Easiest - Recommended ✨)

**Step 1:** Install kagglehub
```bash
pip install kagglehub
```

**Step 2:** Download dataset (no API key needed, automatic!)
```bash
cd /Users/apple/MLOP
/Users/apple/MLOP/.venv/bin/python src/data_acquisition.py
```

That's it! kagglehub will handle everything automatically.

**What happens:**
- Automatically authenticates with your Kaggle account
- Downloads all images (~7,400 images)
- Extracts and organizes into train/test folders
- Creates class subdirectories
- Generates `dataset_stats.json`

Expected time: **10-20 minutes**

---

### Option 2: Using Kaggle API (Alternative)

**Step 1:** Install Kaggle CLI
```bash
pip install kaggle
```

**Step 2:** Set up Kaggle credentials
1. Go to https://www.kaggle.com/settings/account
2. Scroll to "API" section
3. Click **"Create New API Token"** (downloads `kaggle.json`)
4. Place `kaggle.json` in `~/.kaggle/`

```bash
# macOS/Linux
mkdir -p ~/.kaggle
cp ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

**Step 3:** Download
```bash
cd /Users/apple/MLOP
/Users/apple/MLOP/.venv/bin/python src/data_acquisition.py
```

---

### Option 3: Manual Download

**Step 1:** Download from Kaggle website
1. Visit: https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset
2. Click **"Download"** button (requires Kaggle login)
3. Wait for ZIP (~300-400 MB)

**Step 2:** Extract
```bash
cd /Users/apple/MLOP
unzip ~/Downloads/brain-tumor-mri-dataset.zip -d data/raw/
```

**Step 3:** Organize (manual)
```bash
# Create class directories
mkdir -p data/train/{Glioma,Meningioma,Pituitary,No_Tumor}
mkdir -p data/test/{Glioma,Meningioma,Pituitary,No_Tumor}

# Copy ~70% to train, ~30% to test by class
```

---

## 📊 Expected Dataset Structure

After downloading, your `data/` folder should have:

```
data/
├── train/
│   ├── Glioma/           (~2,400 images)
│   ├── Meningioma/       (~1,500 images)
│   ├── Pituitary/        (~1,800 images)
│   └── No_Tumor/         (~1,100 images)
├── test/
│   ├── Glioma/           (~700 images)
│   ├── Meningioma/       (~500 images)
│   ├── Pituitary/        (~600 images)
│   └── No_Tumor/         (~300 images)
└── uploads/              (for retraining - empty initially)
```

**Total: ~7,400 MRI images across 4 tumor classes**

---

## ✅ Verify Download

After downloading, verify the data:

```bash
# Count total images
find data/train -type f -name "*.jpg" | wc -l  # Should be ~5,700
find data/test -type f -name "*.jpg" | wc -l   # Should be ~1,700

# Check class distribution
du -sh data/train/*/
du -sh data/test/*/

# Check image resolution (should be 512x512)
python -c "from PIL import Image; img = Image.open('data/train/Glioma/'$(ls data/train/Glioma | head -1)); print(f'Resolution: {img.size}')"
```

---

## 🚀 Next Steps

After downloading the dataset:

### Option A: Train Model Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run Jupyter notebook to train/evaluate
jupyter notebook notebook/brain_tumor_mri.ipynb
```

### Option B: Use Pre-trained Model
```bash
# Models are already saved in models/ directory
# Start API + UI
/Users/apple/MLOP/.venv/bin/python src/api.py    # Terminal 1
streamlit run deploy/ui.py                       # Terminal 2

# Visit: http://localhost:8501
```

### Option C: Docker (Recommended for demo)
```bash
# Builds containers with all dependencies
docker-compose up --build

# Access:
# - UI: http://localhost:8501
# - API Docs: http://localhost/docs
# - API: http://localhost
```

---

## 🔧 Troubleshooting

### "kagglehub authentication failed"
```bash
# kagglehub should auto-authenticate on first use
# If it doesn't work, check:
# 1. You're logged into Kaggle in your browser
# 2. Run: python -m kagglehub
# 3. If prompted, authenticate and try again
```

### "Dataset not found" error
- Check dataset URL: https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset
- Ensure you have Kaggle account
- Try logging out/in on Kaggle website

### "Download too slow"
- Normal for 300-400 MB dataset
- Expected time: 10-20 minutes
- Don't interrupt the download

### "Not enough disk space"
- Need at least 1-2 GB free
- Check: `df -h`
- Clean up if needed

---

## 📞 Dataset Info

**Source:** https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset

**Medical Context:**
- Glioma: Malignant brain tumor from glial cells
- Meningioma: Tumor arising from brain membrane
- Pituitary: Tumor of pituitary gland
- No Tumor: Normal brain MRI scans

---

**✅ Status: Ready to download!**

Recommended: Use kagglehub for automatic downloading:
```bash
/Users/apple/MLOP/.venv/bin/python src/data_acquisition.py
```

