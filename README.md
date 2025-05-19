Here’s a clean and professional README description for your project:

---

Object Measurement Tool is a web-based application built with Streamlit and OpenCV that allows users to upload an image and automatically detect and measure the dimensions of objects within it. The tool calculates width, height, and area in real-world units (cm) using a fixed pixel-per-cm scale. It displays bounding boxes over detected objects and generates a downloadable CSV report of all measurements.

Ideal for quick dimension estimation in manufacturing, packaging, education, or any domain where non-contact object measurement is helpful.
# 📏 Object Measurement Tool

A simple Streamlit web app that allows users to upload an image and automatically measure the dimensions (width, height, area) of detected objects. Designed with a black-and-white gradient UI, it processes images using OpenCV and generates a downloadable measurement report.

---

## 🚀 Features

- Upload any image (.jpg, .jpeg, .png)
- Detect objects using edge and contour detection
- Estimate dimensions using a predefined scale (pixels per cm)
- Draw bounding boxes and overlay them on the image
- Generate and download a CSV report of measured objects
- Stylish dark theme with modern UI

---

## 🛠️ Technologies Used

- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [OpenCV](https://opencv.org/)
- [NumPy](https://numpy.org/)
- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/object-measurement-app.git
cd object-measurement-app
pip install -r requirements.txt
