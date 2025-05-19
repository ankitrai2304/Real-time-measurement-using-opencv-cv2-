import streamlit as st
import cv2
import numpy as np
import tempfile
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="centered", page_title="Object Measurement", page_icon="📏")

st.markdown("""
<style>
    body {
        background: linear-gradient(135deg, #000000, #434343);
        color: white;
    }
    .stApp {
        background: linear-gradient(to bottom right, #000000, #434343);
        color: white;
    }
    .css-1d391kg, .css-1v3fvcr {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📏 Object Measurement Tool")
st.write("Upload an image with a reference object to measure dimensions (length & breadth). Height requires side view or additional input.")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tfile:
        tfile.write(uploaded_file.read())
        image_path = tfile.name

    image = cv2.imread(image_path)
    if image is None:
        st.error("Failed to read the uploaded image. Please upload a valid image file.")
        st.stop()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    st.image(image_rgb, caption="Uploaded Image", use_column_width=True)

    PIXELS_PER_CM = 10.0

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

    st.image(image_rgb, caption="Measured Objects", use_column_width=True)

    if results:
        df = pd.DataFrame(results)
        st.subheader("📄 Measurement Report")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode()
        st.download_button("📥 Download Report", data=csv, file_name="measurement_report.csv", mime="text/csv")
    else:
        st.warning("No measurable objects detected in the image.")