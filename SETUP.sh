#!/bin/bash
# Installation and Setup Guide

echo "=========================================="
echo "Brain Tumor MRI MLOps Pipeline Setup"
echo "=========================================="
echo ""

# 1. Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# 2. Download dataset
echo "📥 Downloading dataset from Kaggle..."
echo "   (Requires Kaggle API credentials)"
echo "   Setup: https://github.com/Kaggle/kaggle-api#api-credentials"
echo ""
read -p "Download dataset now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python src/data_acquisition.py
fi
echo ""

# 3. Create logs directory
mkdir -p logs/locust_results
echo "✓ Log directories created"
echo ""

echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1️⃣  Train model (Jupyter Notebook):"
echo "   jupyter notebook notebook/brain_tumor_mri.ipynb"
echo ""
echo "2️⃣  Run API server:"
echo "   python src/api.py"
echo ""
echo "3️⃣  Run Streamlit UI (in another terminal):"
echo "   streamlit run deploy/ui.py"
echo ""
echo "4️⃣  Or run with Docker:"
echo "   docker-compose up --build"
echo ""
echo "5️⃣  Load testing:"
echo "   locust -f locustfile.py --host=http://localhost:8000"
echo ""
