import cv2
import numpy as np
import face_recognition
from tensorflow.keras.models import load_model
import pickle
import pymysql
from datetime import datetime, timedelta
import csv
import os

# Configuration
IMAGE_SIZE = (100, 100)
MODEL_FILE = "Files/face_recognition_model.keras"
LABEL_ENCODER_FILE = "Files/label_encoder.pkl"
RESIZE_WIDTH = 320
RESIZE_HEIGHT = 240
CONFIDENCE_THRESHOLD = 0.99  # Confidence level
CAMERA = 0

# Database Configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'facerecognition'

# Cooldown period for attendance
COOLDOWN_TIME = timedelta(minutes=1)

# Global attendance tracking
last_attendance_time = {}


def load_label_encoder():
    """Load the label encoder from a file."""
    with open(LABEL_ENCODER_FILE, 'rb') as f:
        return pickle.load(f)


def get_student_info(student_id):
    """Fetch student information from the database."""
    try:
        connection = pymysql.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        cursor = connection.cursor()
        cursor.execute("SELECT student_id, first_name, last_name, parent_email FROM students WHERE student_id = %s",
                       (student_id,))
        return cursor.fetchone()
    finally:
        if connection:
            connection.close()


def mark_attendance(student_id):
    """Mark attendance for a student by writing to a CSV file."""
    current_time = datetime.now()
    date_str = current_time.strftime("%Y-%m-%d")
    time_str = current_time.strftime("%H:%M:%S")
    csv_filename = f"csv/{date_str}.csv"

    student_info = get_student_info(student_id)
    if not student_info:
        print(f"Student with ID {student_id} not found in the database.")
        return

    first_name, last_name, parent_email = student_info[1], student_info[2], student_info[3]
    attendance_record = {
        "Student ID": student_id,
        "First Name": first_name,
        "Last Name": last_name,
        "Parent Email": parent_email,
        "Date": date_str,
        "Time": time_str,
        "Status": "Present"
    }

    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=attendance_record.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(attendance_record)

    print(f"Attendance marked for {first_name} {last_name} ({parent_email}).")


def can_mark_attendance(student_id):
    """Check if attendance can be marked for a student within the cooldown period."""
    current_time = datetime.now()
    last_time = last_attendance_time.get(student_id)

    if not last_time or current_time - last_time >= COOLDOWN_TIME:
        last_attendance_time[student_id] = current_time
        return True

    return False


def recognize_faces(frame, model, label_encoder):
    """Recognize faces in the frame using the model and label encoder."""
    rgb_frame = frame[:, :, ::-1]
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        face_encoding = np.expand_dims(face_encoding, axis=0)
        preds = model.predict(face_encoding)
        class_idx = np.argmax(preds, axis=1)[0]
        confidence = preds[0][class_idx]

        if confidence > CONFIDENCE_THRESHOLD:
            student_id = int(label_encoder.inverse_transform([class_idx])[0])  # Student ID as label
            text = f"{student_id} ({confidence * 100:.2f}%)"

            if can_mark_attendance(student_id):
                mark_attendance(student_id)
            else:
                print(f"Attendance for {student_id} already marked recently.")
        else:
            text = "Unknown"

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, text, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    return frame


def run_recognition():
    """Run the face recognition system and yield frames for Streamlit."""
    model = load_model(MODEL_FILE)
    label_encoder = load_label_encoder()

    cap = cv2.VideoCapture(CAMERA)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, RESIZE_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RESIZE_HEIGHT)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            frame = recognize_faces(frame, model, label_encoder)
            yield frame  # Yield frame for external use (e.g., Streamlit)

    finally:
        cap.release()

if __name__ == "__main__":
    run_recognition()
