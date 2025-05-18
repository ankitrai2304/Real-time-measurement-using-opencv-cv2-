import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

def main():
    st.title("Object Measurement Tool")
    st.write("Upload an image to measure objects. Include a reference object of known width (preferably a credit card or similar).")
    
    # File uploader for image
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    # Reference object width input (in cm)
    reference_width = st.number_input("Enter the width of reference object in cm (default: 8.56cm for credit card)", 
                                     min_value=0.1, value=8.56, step=0.1)
    
    if uploaded_file is not None:
        # Convert uploaded file to OpenCV format
        image = Image.open(uploaded_file)
        image = np.array(image)
        
        # Make a copy for drawing
        original_image = image.copy()
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply GaussianBlur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edged = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort contours by area (largest first)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
        
        # Display image with found contours
        contour_image = original_image.copy()
        cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 2)
        st.image(contour_image, caption="Detected Objects", use_column_width=True)
        
        # Allow user to select reference object
        st.write("### Select Reference Object")
        st.write("Please select the contour number that corresponds to your reference object (like a credit card):")
        
        reference_idx = st.selectbox("Reference object contour number", 
                                    options=list(range(min(5, len(contours)))), 
                                    format_func=lambda x: f"Contour {x+1}")
        
        if reference_idx is not None and contours:
            # Get the reference contour
            reference_contour = contours[reference_idx]
            
            # Get bounding rectangle of reference object
            ref_x, ref_y, ref_w, ref_h = cv2.boundingRect(reference_contour)
            
            # Draw the reference object
            result_image = original_image.copy()
            cv2.rectangle(result_image, (ref_x, ref_y), (ref_x + ref_w, ref_y + ref_h), (0, 255, 0), 2)
            cv2.putText(result_image, "Reference Object", (ref_x, ref_y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Calculate pixels per cm
            pixels_per_cm = ref_w / reference_width
            
            # Now measure other objects
            st.write("### Measure Other Objects")
            object_idx = st.selectbox("Select object to measure", 
                                     options=list(range(min(10, len(contours)))), 
                                     format_func=lambda x: f"Object {x+1}")
            
            if object_idx is not None:
                # Get the selected object contour
                object_contour = contours[object_idx]
                
                # Get bounding rectangle
                obj_x, obj_y, obj_w, obj_h = cv2.boundingRect(object_contour)
                
                # Calculate real-world dimensions
                width_cm = obj_w / pixels_per_cm
                height_cm = obj_h / pixels_per_cm
                
                # Draw the object with measurements
                cv2.rectangle(result_image, (obj_x, obj_y), (obj_x + obj_w, obj_y + obj_h), (0, 0, 255), 2)
                cv2.putText(result_image, f"Width: {width_cm:.1f}cm", (obj_x, obj_y - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                cv2.putText(result_image, f"Height: {height_cm:.1f}cm", (obj_x, obj_y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                st.image(result_image, caption="Object Measurements", use_column_width=True)
                
                # Display measurements in text form as well
                st.write(f"### Measurement Results:")
                st.write(f"- Width: {width_cm:.2f} cm")
                st.write(f"- Height: {height_cm:.2f} cm")
                
                # Calculate area if appropriate
                area_cm2 = width_cm * height_cm
                st.write(f"- Approximate Area: {area_cm2:.2f} cm²")
                
                # Advanced options
                if st.checkbox("Show advanced measurement options"):
                    # Calculate perimeter
                    perimeter_pixels = cv2.arcLength(object_contour, True)
                    perimeter_cm = perimeter_pixels / pixels_per_cm
                    st.write(f"- Perimeter: {perimeter_cm:.2f} cm")
                    
                    # Minimum enclosing circle
                    (x, y), radius = cv2.minEnclosingCircle(object_contour)
                    radius_cm = radius / pixels_per_cm
                    st.write(f"- Equivalent Circle Radius: {radius_cm:.2f} cm")
                    
                    # Aspect ratio
                    aspect_ratio = width_cm / height_cm if height_cm > 0 else 0
                    st.write(f"- Aspect Ratio (width/height): {aspect_ratio:.2f}")

    
    with st.expander("How to use this app"):
        st.write("""
        1. Upload an image containing objects you want to measure
        2. Make sure the image includes a reference object with known dimensions (e.g., credit card = 8.56cm width)
        3. Select the contour number corresponding to your reference object
        4. Select other objects to measure
        5. The app will calculate and display real-world measurements
        
        For best results:
        - Ensure good lighting with minimal shadows
        - Place objects on a contrasting background 
        - Position camera directly above objects (bird's eye view)
        - Keep objects separated from each other
        - Make sure the reference object is in the same plane as objects to be measured
        """)

if __name__ == "__main__":
    main()