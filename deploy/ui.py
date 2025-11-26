"""
Streamlit Web UI for Brain Tumor MRI Classifier - FIXED VERSION
"""

UI_VERSION = "ui-1.2.0"

import streamlit as st

st.set_page_config(
    page_title="Brain Tumor MRI Classifier",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern, readable styling
st.markdown(
        """
        <style>
            /* Base backgrounds */
            .stApp, [data-testid="stAppViewContainer"], body { background: #ffffff; }

            /* Cards */
            .card {
                border: 1px solid #e6e9ef;
                border-radius: 12px;
                background: #ffffff;
                box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
                padding: 16px 18px;
                margin-bottom: 16px;
            }
            .card-header {
                font-weight: 600; font-size: 1.05rem; margin-bottom: 8px;
            }
            .subtle {
                color: #667085; font-size: 0.92rem; margin-top: -4px; margin-bottom: 8px;
            }

            /* Buttons */
            .stButton > button {
                border: 1px solid #d0d5dd !important;
                border-radius: 10px !important;
                padding: 0.5rem 0.9rem !important;
                box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05) !important;
            }

            /* File uploader */
            [data-testid="stFileUploader"] {
                border: 1px dashed #d0d5dd; border-radius: 12px; padding: 10px 12px;
                background: #fafafa;
            }

            /* Images */
            .stImage img { border-radius: 10px; border: 1px solid #e6e9ef; }

            /* Metrics */
            [data-testid="stMetric"] { border: 1px solid #e6e9ef; border-radius: 12px; padding: 8px 10px; }
        </style>
        """,
        unsafe_allow_html=True,
)

import requests
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os

# UI helpers
def card_open(title=None, subtitle=None):
    seg = '<div class="card">'
    if title:
        seg += f'<div class="card-header">{title}</div>'
    if subtitle:
        seg += f'<div class="subtle">{subtitle}</div>'
    st.markdown(seg, unsafe_allow_html=True)

def card_close():
    st.markdown('</div>', unsafe_allow_html=True)

# API Configuration - Auto-detect environment
# Render deployment: use new brain-tumor-api service
# Docker deployment: use nginx
# Local deployment: use localhost
if os.getenv("GCP_API_URL"):
    API_URL = os.getenv("GCP_API_URL")  # Use env var if set (legacy)
elif os.getenv("DOCKER_ENV") == "true":
    API_URL = "http://nginx:80"  # Docker internal network
else:
    # Render cloud deployment - brain-tumor-api service
    API_URL = os.getenv("API_URL", "https://brain-tumor-api-xc9w.onrender.com")

@st.cache_data(ttl=60)
def check_api_health():
    """Check if API is running. Render free tier may need time to wake up."""
    try:
        # Try with longer timeout for Render free tier (needs ~30s to wake from sleep)
        response = requests.get(f"{API_URL}/health", timeout=50)
        return response.status_code == 200
    except Exception as e:
        return False

# Sidebar
st.sidebar.title("Brain Tumor MRI Classifier")
st.sidebar.markdown("---")

# Show status - lazy load
api_status_placeholder = st.sidebar.empty()

# Function to display API status
def update_api_status():
    api_healthy = check_api_health()
    if api_healthy:
        api_status_placeholder.success("API Connected")
        return True
    else:
        api_status_placeholder.warning("API Not Available - Waking up on first request...")
        return False

api_healthy = update_api_status()
# Show current API endpoint for debugging/visibility
with st.sidebar:
    st.caption("API Endpoint")
    st.code(API_URL, language="text")
    st.caption(f"UI Version: {UI_VERSION}")

# Main tabs
tab1, tab_vis, tab2, tab3, tab4 = st.tabs([
    "Predict",
    "Visualizations",
    "Upload & Retrain",
    "Model Info",
    "Admin"
])

# ============================================================================
# TAB 1: PREDICTION
# ============================================================================
with tab1:
    st.header("Single Image Prediction")
    st.markdown("Upload a brain MRI image to get a tumor classification prediction.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        card_open("Upload Image", "JPG or PNG recommended")
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=["jpg", "jpeg", "png"],
            key="predict_file"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True, caption="Uploaded Image")
        card_close()
    
    with col2:
        card_open("Prediction Result", "Model output and confidence")
        
        if uploaded_file is not None:
            if st.button("Predict", key="predict_btn"):
                with st.spinner("Analyzing image... (may take 30+ seconds on first request)"):
                    try:
                        # Provide filename and content-type for FastAPI UploadFile parsing
                        file_bytes = uploaded_file.getvalue()
                        mime = getattr(uploaded_file, "type", None) or "image/jpeg"
                        files = {"file": (uploaded_file.name or "upload.jpg", file_bytes, mime)}
                        response = requests.post(
                            f"{API_URL}/predict",
                            files=files,
                            timeout=60  # Longer timeout for Render cold start
                        )
                        
                        # Prefer JSON; if HTML returned, surface a clearer message
                        if response.status_code == 200 and response.headers.get("content-type", "").startswith("application/json"):
                            result = response.json()
                            
                            st.success("Prediction Complete!")
                            
                            # Display prediction
                            predicted_class = result['predicted_class']
                            confidence = result['confidence']
                            
                            st.metric(
                                "Predicted Class",
                                predicted_class,
                                f"{confidence*100:.1f}%"
                            )
                            
                            st.metric(
                                "Inference Time",
                                f"{result['inference_time_ms']:.1f}ms"
                            )
                            
                            # Probabilities
                            st.subheader("Class Probabilities")
                            probs = result['probabilities']
                            
                            prob_df = pd.DataFrame({
                                'Class': list(probs.keys()),
                                'Probability': list(probs.values())
                            }).sort_values('Probability', ascending=False)
                            
                            fig, ax = plt.subplots(figsize=(10, 5))
                            colors = ['#667eea' if p == max(probs.values()) else '#4ECDC4' for p in prob_df['Probability']]
                            ax.barh(prob_df['Class'], prob_df['Probability'], color=colors)
                            ax.set_xlabel('Probability')
                            ax.set_title('Prediction Confidence by Class', fontweight='bold')
                            st.pyplot(fig, use_container_width=True)
                        else:
                            ct = response.headers.get("content-type", "")
                            if "html" in ct.lower():
                                st.error("Prediction failed: received HTML page instead of JSON. This usually means the API URL is incorrect or the API is still waking up. Please retry in 30s.")
                            else:
                                st.error(f"Prediction failed ({response.status_code}): {response.text}")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            st.info("Upload an image to get started")
            card_close()

# ============================================================================
# TAB 2: UPLOAD & RETRAIN
# ============================================================================
with tab2:
    st.header("Upload Data & Trigger Retraining")
    st.markdown("Upload images and retrain the model on new data.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        card_open("Upload Images", "Store under data/uploads/{label}/")
        
        disease_label = st.selectbox(
            "Select disease class",
            ["Glioma", "Meningioma", "Pituitary", "No_Tumor"],
            key="upload_label"
        )
        
        uploaded_files = st.file_uploader(
            "Choose images",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="upload_files"
        )
        
        if uploaded_files and api_healthy:
            if st.button("Upload Files", key="upload_btn"):
                with st.spinner(f"Uploading {len(uploaded_files)} file(s)..."):
                    try:
                        files = [("files", (f.name, f.getvalue(), "image/jpeg")) for f in uploaded_files]
                        response = requests.post(
                            f"{API_URL}/upload_training_data?label={disease_label}",
                            files=files,
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"Uploaded {result.get('uploaded_count', 0)} files!")
                        else:
                            st.error(f"Upload failed: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        card_close()
    
    with col2:
        card_open("Trigger Retraining", "Starts a mock training job")
        
        epochs = st.slider("Training Epochs", 1, 20, 5)
        batch_size = st.slider("Batch Size", 8, 64, 32)
        learning_rate = st.selectbox("Learning Rate", [1e-3, 1e-4, 1e-5], format_func=lambda x: f"{x:.0e}")
        
        if st.button("Start Retrain", key="retrain_btn") and api_healthy:
            with st.spinner("Starting retraining job..."):
                try:
                    payload = {
                        "epochs": epochs,
                        "batch_size": batch_size,
                        "learning_rate": float(learning_rate)
                    }
                    response = requests.post(
                        f"{API_URL}/retrain",
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        job_id = result['job_id']
                        st.success(f"Retrain job started: {job_id}")
                        st.info(f"Status: {result['status']}")
                        
                        # Auto-check status
                        st.markdown("---")
                        st.subheader("Training Status")
                        
                        with st.spinner("Checking training status..."):
                            import time
                            time.sleep(2)
                            status_response = requests.get(
                                f"{API_URL}/retrain_status/{job_id}",
                                timeout=10
                            )
                            
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                
                                col_status1, col_status2, col_status3 = st.columns(3)
                                
                                with col_status1:
                                    st.metric("Job Status", status_data['status'].upper())
                                
                                with col_status2:
                                    accuracy = status_data.get('accuracy')
                                    if accuracy is not None:
                                        st.metric("Accuracy", f"{accuracy*100:.1f}%")
                                    else:
                                        st.metric("Accuracy", "Calculating...")
                                
                                with col_status3:
                                    loss = status_data.get('loss')
                                    if loss is not None:
                                        st.metric("Loss", f"{loss:.4f}")
                                    else:
                                        st.metric("Loss", "Calculating...")
                                
                                model_version = status_data.get('model_version', 'v2')
                                st.success(f"Model Updated to Version {model_version}")
                                
                                if status_data['status'] == 'completed':
                                    st.balloons()
                                    completed_at = status_data.get('completed_at', 'now')
                                    st.info(f"🎉 Training completed at {completed_at}")
                            
                    else:
                        st.error(f"Failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            card_close()

# ============================================================================
# TAB 3: MODEL INFO
# ============================================================================
with tab3:
    st.header("Model Information")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        card_open("Model Details")
        st.write("""
        - **Framework**: TensorFlow/Keras
        - **Architecture**: MobileNetV2
        - **Input Size**: 224x224
        - **Training Epochs**: 15
        - **Optimizer**: Adam
        - **Loss**: Categorical Crossentropy
        """)
        card_close()
    
    with info_col2:
        card_open("Classes")
        st.write("""
        1. **Glioma Tumor** - Most common brain tumor
        2. **Meningioma Tumor** - Tumor of brain membrane
        3. **Pituitary Tumor** - Hormone-producing tumor
        4. **No Tumor** - Healthy brain
        """)
        card_close()
    
    st.divider()
    
    card_open("Performance Metrics")
    st.write("""
    - **Accuracy**: 96%+
    - **Precision**: 95%+
    - **Recall**: 94%+
    - **F1-Score**: 94%+
    """)
    card_close()

# ============================================================================
# TAB 4: ADMIN
# ============================================================================
with tab4:
    st.header("Admin & Status")
    
    card_open("API Health")
    if st.button("🔍 Check API Health"):
        if api_healthy:
            try:
                response = requests.get(f"{API_URL}/health", timeout=5)
                data = response.json()
                st.success("API is healthy")
                st.json(data)
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("API not available")
    card_close()

    card_open("Retrain Jobs")
    if st.button("View Retrain Jobs"):
        if api_healthy:
            try:
                response = requests.get(f"{API_URL}/retrain_jobs", timeout=5)
                data = response.json()
                st.json(data)
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("API not available")
    card_close()

    st.divider()
    
    card_open("📝 Logs")
    st.write("""
    API logs are available at:
    - File: `/Users/apple/MLOP/logs/api.log`
    - Training artifacts in: `/Users/apple/MLOP/logs/`
    """)
    card_close()

# ============================================================================
# TAB VISUALIZATIONS
# ============================================================================
with tab_vis:
    st.header("Dataset Visualizations")
    st.markdown("Class distribution, average brightness, and resolution from the dataset stats.")

    if api_healthy:
        try:
            resp = requests.get(f"{API_URL}/dataset_stats", timeout=15)
            if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("application/json"):
                data = resp.json()

                # Class distribution
                card_open("Class Distribution")
                cd = data.get("class_distribution", {})
                if cd:
                    df = pd.DataFrame({"Class": list(cd.keys()), "Count": list(cd.values())})
                    st.bar_chart(df.set_index("Class"))
                else:
                    st.info("No class distribution available.")
                card_close()

                # Average brightness
                card_open("Average Brightness by Class")
                ab = data.get("avg_brightness_by_class", {})
                if ab:
                    df2 = pd.DataFrame({"Class": list(ab.keys()), "Brightness": list(ab.values())})
                    st.bar_chart(df2.set_index("Class"))
                else:
                    st.info("No brightness stats available.")
                card_close()

                # Resolution
                card_open("Average Image Resolution")
                ar = data.get("avg_resolution", {})
                w = ar.get("width", 0)
                h = ar.get("height", 0)
                st.metric("Avg Width", w)
                st.metric("Avg Height", h)
                card_close()
            else:
                st.error(f"Failed to fetch dataset stats ({resp.status_code}).")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("API not available yet — check again in a moment.")
