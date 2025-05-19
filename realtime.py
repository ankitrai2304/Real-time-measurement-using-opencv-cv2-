import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import os

st.set_page_config(page_title="Object Measurement Tool", layout="wide")

def main():
    st.title("Object Measurement Tool")
    st.write("Upload an image and draw lines to measure objects")
    
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        image = np.array(image)
        
        working_image = image.copy()
        height, width = working_image.shape[:2]
        
        col1, col2 = st.columns([2, 1])
        
        with col2:
            st.subheader("Reference Measurement")
            st.write("1. Draw a reference line on a known object")
            st.write("2. Enter the real-world length of that line")
            
            reference_length = st.number_input(
                "Reference length (cm)", 
                min_value=0.1, 
                value=10.0, 
                step=0.1,
                help="The real-world length of your reference line in centimeters"
            )
            
            st.subheader("Draw Lines")
            st.write("Click and drag to draw measurement lines")
            
            clear_button = st.button("Clear All Lines")
            
            st.subheader("Measurements")
            measurements_placeholder = st.empty()
            
        if 'points' not in st.session_state:
            st.session_state.points = []
        if 'ref_points' not in st.session_state:
            st.session_state.ref_points = []
        if 'ref_set' not in st.session_state:
            st.session_state.ref_set = False
        if 'drawing_ref' not in st.session_state:
            st.session_state.drawing_ref = True
        if 'measurements' not in st.session_state:
            st.session_state.measurements = []
            
        if clear_button:
            st.session_state.points = []
            st.session_state.ref_points = []
            st.session_state.ref_set = False
            st.session_state.drawing_ref = True
            st.session_state.measurements = []
            
        with col1:
            canvas_result = st_canvas(image, height=height, width=width)
            
        if canvas_result.json_data is not None:
            objects = canvas_result.json_data["objects"]
            
            for obj in objects:
                if obj["type"] == "line":
                    start_x, start_y = obj["x1"], obj["y1"]
                    end_x, end_y = obj["x2"], obj["y2"]
                    
                    if not st.session_state.ref_set:
                        pixel_distance = np.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
                        # Calculate pixels per cm using known reference length
                        st.session_state.pixels_per_cm = pixel_distance / reference_length
                        st.session_state.ref_points = [(start_x, start_y), (end_x, end_y)]
                        st.session_state.ref_set = True
                        st.session_state.drawing_ref = False
                    else:
                        if [(start_x, start_y), (end_x, end_y)] not in st.session_state.points:
                            st.session_state.points.append([(start_x, start_y), (end_x, end_y)])
                            
                            pixel_distance = np.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
                            cm_distance = pixel_distance / st.session_state.pixels_per_cm
                            st.session_state.measurements.append(cm_distance)
            
        result_image = working_image.copy()
        
        if st.session_state.ref_set and len(st.session_state.ref_points) == 2:
            start, end = st.session_state.ref_points
            cv2.line(result_image, 
                    (int(start[0]), int(start[1])), 
                    (int(end[0]), int(end[1])), 
                    (0, 255, 0), 2)
            cv2.putText(result_image, 
                       f"Reference: {reference_length:.1f} cm", 
                       (int(start[0]), int(start[1] - 10)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
        for i, (points, measurement) in enumerate(zip(st.session_state.points, st.session_state.measurements)):
            start, end = points
            cv2.line(result_image, 
                    (int(start[0]), int(start[1])), 
                    (int(end[0]), int(end[1])), 
                    (0, 0, 255), 2)
            cv2.putText(result_image, 
                       f"{measurement:.1f} cm", 
                       (int(start[0]), int(start[1] - 10)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
        col1.image(result_image, use_column_width=True)
        
        measurements_text = ""
        if st.session_state.ref_set:
            measurements_text += f"Reference: {reference_length:.2f} cm\n\n"
            
            for i, measurement in enumerate(st.session_state.measurements):
                measurements_text += f"Line {i+1}: {measurement:.2f} cm\n"
                
            measurements_placeholder.text_area("Results", measurements_text, height=200)
            
        if not st.session_state.ref_set:
            col1.info("First, draw a reference line on an object with known length")
        else:
            col1.info("Now draw lines to measure other objects")
            
    with st.expander("How to use this app"):
        st.write("""
        1. Upload an image containing objects you want to measure
        2. Draw a line on an object with known dimensions (e.g., a ruler, credit card, etc.)
        3. Enter the real-world length of that line in centimeters
        4. Draw additional lines on objects you want to measure`
        5. The app will calculate and display real-world measurements
        
        For best results:
        - Ensure good lighting with minimal shadows
        - Keep the camera perpendicular to the objects being measured
        - Use a clear reference object
        - Ensure all objects are in the same plane for accurate measurements
        """)
def st_canvas(image, height, width):
    image_placeholder = st.empty()
    image_placeholder.image(image, use_column_width=True)
    
    st.write("Enter coordinates manually:")
    
    col1, col2 = st.columns(2)
    with col1:
        start_x = st.number_input("Start X", min_value=0, max_value=width, value=width//4)
        start_y = st.number_input("Start Y", min_value=0, max_value=height, value=height//2)
    with col2:
        end_x = st.number_input("End X", min_value=0, max_value=width, value=(width*3)//4)
        end_y = st.number_input("End Y", min_value=0, max_value=height, value=height//2)
    
    draw_line = st.button(
        "Draw Line" if st.session_state.drawing_ref else "Draw Measurement Line"
    )
    result = type('obj', (object,), {
        'json_data': {
            'objects': []
        }
    })
    
    if draw_line:
        result.json_data["objects"].append({
            "type": "line",
            "x1": start_x,
            "y1": start_y,
            "x2": end_x,
            "y2": end_y
        })
        
        temp_img = image.copy()
        color = (0, 255, 0) if st.session_state.drawing_ref else (0, 0, 255)
        cv2.line(temp_img, (start_x, start_y), (end_x, end_y), color, 2)
        image_placeholder.image(temp_img, use_column_width=True)
    
    return result

if __name__ == "__main__":
    main()
