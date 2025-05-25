import streamlit as st
import cv2
import numpy as np
import tempfile
import pandas as pd

# Page configuration
st.set_page_config(layout="centered", page_title="AR Measure_Pro", page_icon="📏")

# Custom UI styling
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(to bottom right, #1f1f1f, #3f3f3f);
            color: white;
            font-family: 'Segoe UI', sans-serif;
        }
        .css-1v3fvcr, .css-1d391kg {
            color: white !important;
        }
        .css-ffhzg2 {
            background-color: #2d2d2d;
            border-radius: 10px;
            padding: 10px;
        }
        .stButton>button {
            color: white;
            background-color: #4CAF50;
            border-radius: 10px;
            font-weight: bold;
        }
        .stDownloadButton>button {
            color: white;
            background-color: #1a73e8;
            border-radius: 10px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📏 AR Measure Pro")
st.markdown("Upload an image with a reference object to **measure dimensions (length & breadth)**. Height measurement requires a side view or additional input.")

# File uploader
with st.expander("📤 Upload Image", expanded=True):
    uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Save the file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tfile:
        tfile.write(uploaded_file.read())
        image_path = tfile.name

    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        st.error("❌ Failed to read the uploaded image. Please try again.")
        st.stop()

    # Preprocess the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Show uploaded image
    with st.expander("🖼 Original Image"):
        st.image(image_rgb, caption="Uploaded Image", width=400) 

    # Measurement logic
    PIXELS_PER_CM = 10.0  # Calibration constant
    results = []

    for i, c in enumerate(contours):
        if cv2.contourArea(c) < 100:
            continue

        rect = cv2.minAreaRect(c)
        (x, y), (w, h), angle = rect

        if w == 0 or h == 0:
            continue

        width_cm = round(w / PIXELS_PER_CM, 2)
        height_cm = round(h / PIXELS_PER_CM, 2)

        box = cv2.boxPoints(rect)
        box = np.intp(box)
        cv2.drawContours(image_rgb, [box], 0, (0, 255, 0), 2)

        results.append({
            "Object #": i + 1,
            "Width (cm)": max(width_cm, height_cm),
            "Height (cm)": min(width_cm, height_cm),
            "Area (cm²)": round(width_cm * height_cm, 2)
        })

    # Show result image
    st.markdown("### ✅ Detection Result")
    st.image(image_rgb, caption="Detected and Measured Objects", width=500) 

    # Show results in a table
    if results:
        df = pd.DataFrame(results)

        with st.expander("📄 Measurement Report", expanded=True):
            st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode()
        st.download_button("📥 Download CSV Report", data=csv, file_name="measurement_report.csv", mime="text/csv")
    else:
        st.warning("⚠️ No measurable objects detected in the image.")
