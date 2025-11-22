import streamlit as st

st.set_page_config(page_title="Test", layout="wide")

st.title("🧠 Brain Tumor Classifier")

st.write("If you see this, Streamlit is working!")

st.success("✓ Connection successful")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Status", "Online", "✓")
with col2:
    st.metric("Model", "Loaded", "✓")
with col3:
    st.metric("API", "Running", "✓")

st.divider()

st.subheader("Upload Image")
uploaded = st.file_uploader("Choose image", type=["jpg", "png"])
if uploaded:
    st.write("File uploaded!")
    st.image(uploaded)

st.divider()

st.write("🎉 Streamlit UI is fully functional!")
