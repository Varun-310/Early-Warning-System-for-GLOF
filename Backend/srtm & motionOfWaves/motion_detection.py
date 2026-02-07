import cv2
import numpy as np
import streamlit as st

# Define a conversion factor (meters per pixel)
PIXEL_TO_METER_CONVERSION = 0.01  # Example: 1 pixel = 0.01 meters

# Define an estimated depth (meters) for the water flow
ESTIMATED_DEPTH = 0.5  # Example: 0.5 meters depth

# Define HSV color ranges for glacial lake colors
glacial_lake_color_ranges = [
    (np.array([75, 50, 50]), np.array([120, 255, 255])),  # Turquoise/Blue-Green
    (np.array([100, 50, 50]), np.array([140, 255, 255])),  # Deep Blue
    (np.array([60, 50, 50]), np.array([80, 255, 255])),    # Emerald Green
    (np.array([90, 20, 150]), np.array([120, 100, 255]))   # Milky Blue/Grayish Blue
]

# Parameters for Optical Flow (Farneback)
params = dict(pyr_scale=0.5, levels=3, winsize=15, iterations=3, poly_n=5, poly_sigma=1.2, flags=0)

def detect_water_flow(cap):
    ret, prev_frame = cap.read()
    if not ret:
        st.error("Failed to capture initial frame!")
        return

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.warning("End of video stream or failed to capture frame!")
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        water_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower, upper in glacial_lake_color_ranges:
            mask = cv2.inRange(hsv, lower, upper)
            water_mask = cv2.bitwise_or(water_mask, mask)

        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, **params)

        magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        motion_mask = magnitude > 1.5
        combined_mask = cv2.bitwise_and(water_mask, motion_mask.astype(np.uint8) * 255)

        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        annotated_frame = frame.copy()
        total_volume = 0

        for contour in contours:
            pixel_area = cv2.contourArea(contour)
            if pixel_area > 100:
                real_world_area = pixel_area * (PIXEL_TO_METER_CONVERSION ** 2)
                volume = real_world_area * ESTIMATED_DEPTH
                total_volume += volume

                x, y, w, h = cv2.boundingRect(contour)
                cv2.drawContours(annotated_frame, [contour], -1, (0, 255, 0), 2)
                cv2.putText(annotated_frame, f"Volume: {volume:.2f} m^3", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        st.image(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB), caption="Glacial Lake Water Flow Detection", channels="RGB")
        st.text(f"Total Water Flow Volume: {total_volume:.2f} m³")

        prev_gray = gray

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def main():
    st.title("Glacial Lake Water Flow Detection")
    source = st.selectbox("Select Video Source", ["Webcam", "IP Camera"])
    ip_url = ""
    if source == "IP Camera":
        ip_url = st.text_input("Enter IP Camera URL", "http://<IP>:<PORT>/video")

    if st.button("Start Detection"):
        cap = cv2.VideoCapture(0 if source == "Webcam" else ip_url)
        if not cap.isOpened():
            st.error("Failed to open video source!")
        else:
            detect_water_flow(cap)
            cap.release()

if __name__ == "__main__":
    main()
