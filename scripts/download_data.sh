#!/bin/bash
 # Download Brain Tumor MRI dataset from Kaggle

echo "📥 Downloading Brain Tumor MRI dataset..."
echo ""
echo "This script requires Kaggle API credentials."
echo "Setup: https://github.com/Kaggle/kaggle-api#api-credentials"
echo ""

# Check if Kaggle API is configured
if [ ! -f ~/.kaggle/kaggle.json ]; then
    echo "❌ Kaggle API credentials not found."
    echo "Please setup your Kaggle API credentials first."
    exit 1
fi

# Download dataset
python ../src/data_acquisition.py

echo "✅ Dataset download complete!"
