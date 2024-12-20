import os
import cv2
import streamlit as st

# Configuration
IMAGE_SIZE = (100, 100)
DATASET_PATH = "captured_faces"
PADDING = 30
NUM_IMAGES = 200
CAMERA = 0

# Function to capture faces and stream video to Streamlit
def capture_faces(name, video_placeholder, num_images=NUM_IMAGES):
    folder_name = os.path.join(DATASET_PATH, name)
    os.makedirs(folder_name, exist_ok=True)

    cap = cv2.VideoCapture(CAMERA)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    count = 0
    st.info("Capturing faces... Press 'q' to exit early.")
    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to grab frame. Ensure the camera is working.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in faces:
            x = max(0, x - PADDING)
            y = max(0, y - PADDING)
            w = min(w + 2 * PADDING, frame.shape[1] - x)
            h = min(h + 2 * PADDING, frame.shape[0] - y)

            face_img = frame[y:y + h, x:x + w]
            face_img = cv2.resize(face_img, IMAGE_SIZE)
            img_path = os.path.join(folder_name, f"{name}_{count + 1}.jpg")
            cv2.imwrite(img_path, face_img)
            count += 1

            if count >= num_images:
                break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_placeholder.image(rgb_frame, channels="RGB")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    st.success(f"✅ Successfully captured {count} faces.")

def run_capture_app(student_id):
    video_placeholder = st.empty()
    capture_faces(student_id, video_placeholder)
    return os.path.join(DATASET_PATH, student_id)
