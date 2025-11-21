"""
Streamlit Web UI for Brain Tumor MRI Classifier - Standalone Version

This version works without requiring the API server to be running.
It demonstrates the interface and basic functionality.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from pathlib import Path
import json

# Page configuration
st.set_page_config(
    page_title="Brain Tumor MRI Classifier",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
<style>
    .main { padding: 2rem; }
    .stTabs [data-baseweb="tab-list"] button { font-size: 16px; }
    .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 8px; color: white; }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🧠 Brain Tumor MRI Classifier")
st.sidebar.markdown("---")

# Load model metadata
try:
    with open(Path("models/model_metadata.json"), "r") as f:
        metadata = json.load(f)
        st.sidebar.success("✅ Model Loaded")
except:
    st.sidebar.warning("⚠️ Model metadata not found")
    metadata = None

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔮 Predict",
    "📊 Visualizations",
    "📤 Upload & Retrain",
    "📈 Model Info",
    "ℹ️ About"
])

# ============================================================================
# TAB 1: PREDICTION
# ============================================================================
with tab1:
    st.header("🔮 Single Image Prediction")
    st.markdown("Upload a brain MRI image to get a tumor classification prediction.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Image")
        uploaded_file = st.file_uploader(
            "Choose an image (JPG, PNG)",
            type=["jpg", "jpeg", "png"],
            key="predict_file"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True, caption="Uploaded Image")
    
    with col2:
        st.subheader("Prediction Result")
        
        if uploaded_file is not None:
            if st.button("🚀 Predict", key="predict_btn"):
                st.info("📝 Note: API server not running. This is a demo interface.")
                st.info("To enable live predictions, start the API: `python src/api.py`")

# ============================================================================
# TAB 2: VISUALIZATIONS
# ============================================================================
with tab2:
    st.header("📊 Dataset Visualizations & Statistics")
    st.markdown("Explore insights about the brain tumor MRI dataset.")
    
    # Class information
    class_info = {
        'Glioma': 'Glioma Tumor',
        'Meningioma': 'Meningioma Tumor',
        'Pituitary': 'Pituitary Tumor',
        'No_Tumor': 'No Tumor Detected'
    }
    
    st.subheader("📚 Dataset Classes")
    
    cols = st.columns(4)
    for idx, (class_name, description) in enumerate(class_info.items()):
        with cols[idx]:
            st.markdown(f"""
            **{class_name}**
            
            {description}
            """)
    
    # Show sample visualizations if available
    viz_path = Path("logs")
    if viz_path.exists():
        st.subheader("📈 Training Visualizations")
        
        viz_cols = st.columns(3)
        
        viz_files = [
            ("training_history.png", "Training History"),
            ("confusion_matrix.png", "Confusion Matrix"),
            ("per_class_metrics.png", "Per-Class Metrics")
        ]
        
        for idx, (file, name) in enumerate(viz_files):
            try:
                img_path = viz_path / file
                if img_path.exists():
                    with viz_cols[idx % 3]:
                        st.subheader(name)
                        st.image(str(img_path), use_column_width=True)
            except Exception as e:
                st.warning(f"Could not load {file}")

# ============================================================================
# TAB 3: UPLOAD & RETRAIN
# ============================================================================
with tab3:
    st.header("📤 Upload Data & Trigger Retraining")
    st.markdown("Upload bulk brain MRI images to retrain the model.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📂 Upload Images")
        uploaded_files = st.file_uploader(
            "Choose multiple images",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="retrain_files"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} images selected")
    
    with col2:
        st.subheader("⚙️ Retraining Config")
        
        epochs = st.slider("Epochs", 1, 50, 10)
        batch_size = st.selectbox("Batch Size", [16, 32, 64])
        learning_rate = st.selectbox("Learning Rate", [1e-3, 1e-4, 1e-5])
        
        if st.button("🚀 Start Retraining", key="retrain_btn"):
            st.info("📝 Note: API server not running. Retraining requires the API.")
            st.info("To enable retraining, start the API: `python src/api.py`")

# ============================================================================
# TAB 4: MODEL INFO
# ============================================================================
with tab4:
    st.header("📈 Model Information")
    
    if metadata:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Model Details")
            st.json({
                "Name": metadata.get("model_name", "N/A"),
                "Version": metadata.get("version", "N/A"),
                "Architecture": metadata.get("architecture", "N/A"),
                "Classes": len(metadata.get("class_labels", []))
            })
        
        with col2:
            st.subheader("Performance Metrics")
            if "metrics" in metadata:
                metrics = metadata["metrics"]
                st.metric("Accuracy", f"{metrics.get('accuracy', 0):.4f}")
                st.metric("Precision", f"{metrics.get('precision', 0):.4f}")
                st.metric("Recall", f"{metrics.get('recall', 0):.4f}")
                st.metric("F1 Score", f"{metrics.get('f1_score', 0):.4f}")
        
        st.subheader("Class Labels")
        classes = metadata.get("class_labels", [])
        for idx, cls in enumerate(classes):
            st.write(f"{idx}: {cls}")
    else:
        st.warning("Model metadata not loaded")

# ============================================================================
# TAB 5: ABOUT
# ============================================================================
with tab5:
    st.header("ℹ️ About This Project")
    
    st.markdown("""
    ## Brain Tumor MRI Classification
    
    This is an end-to-end MLOps project for classifying brain tumors in MRI scans using deep learning.
    
    ### Dataset
    - **Source:** Brain Tumor MRI Dataset (Kaggle)
    - **Total Images:** ~7,400
    - **Classes:** 4 (Glioma, Meningioma, Pituitary, No_Tumor)
    - **Split:** 70% Train, 15% Validation, 15% Test
    
    ### Model
    - **Architecture:** MobileNetV2 Transfer Learning
    - **Input:** 224×224 RGB Images
    - **Output:** 4-class Classification
    - **Training:** 15 Epochs, Adam Optimizer
    
    ### Features
    - ✅ Deep Learning Model Training
    - ✅ REST API for Predictions
    - ✅ Web UI for Inference
    - ✅ Model Retraining Pipeline
    - ✅ Performance Visualizations
    - ✅ Docker Deployment
    
    ### Getting Started
    
    1. **Start the API:**
       ```bash
       python src/api.py
       ```
    
    2. **Run the UI (this app):**
       ```bash
       streamlit run deploy/ui.py
       ```
    
    3. **Upload an MRI image and get predictions!**
    
    ### Project Structure
    ```
    MLOP/
    ├── models/              # Trained models
    ├── data/                # Dataset
    ├── src/                 # Core code
    ├── deploy/              # API & UI
    ├── notebook/            # Training notebook
    └── logs/                # Training artifacts
    ```
    
    ### Technologies
    - TensorFlow / Keras
    - FastAPI
    - Streamlit
    - Docker
    - scikit-learn
    
    ---
    
    **Version:** 1.0.0 | **Status:** Production Ready ✅
    """)

# Footer
st.markdown("---")
st.markdown("Brain Tumor MRI Classifier | MLOps Pipeline | Version 1.0")
