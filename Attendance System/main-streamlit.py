import os
import cv2
import streamlit as st
import mysql.connector
from datetime import datetime, time
import FaceCapture
import Encoding
import Recognizer
import pre_processing
from Train_Model import train_encodings
# import insert_attendance
import time
import send_email
import pandas as pd

# Database connection details
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "facerecognition"

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Apply CSS
local_css("styles.css")
def fetch_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT student_id, first_name, last_name, date_of_birth, class_id, parent_email
        FROM students
    """)
    students = cursor.fetchall()
    conn.close()
    return pd.DataFrame(students,
                        columns=["Student ID", "First Name", "Last Name", "Date of Birth", "Class ID", "Parent Email"])


# Function to fetch parent details from the database
def fetch_parents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT parent_firstname, parent_lastname, email, phone_number, student_id
        FROM parent
    """)
    parents = cursor.fetchall()
    conn.close()
    return pd.DataFrame(parents,
                        columns=["Parent First Name", "Parent Last Name", "Email", "Phone Number", "Student ID"])


# Function to fetch class details from the database
def fetch_class_details():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT class_id, class_name
        FROM class
    """)
    classes = cursor.fetchall()
    conn.close()
    return pd.DataFrame(classes, columns=["Class ID", "Class Name"])


# Function to fetch attendance details from the database
def fetch_attendance():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT attendance_id, student_id, date, status
        FROM attendance
    """)
    attendance = cursor.fetchall()
    conn.close()
    return pd.DataFrame(attendance, columns=["Attendance ID", "Student ID", "Date", "Status"])


# Streamlit app section for displaying tables


# Connect to the database
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


# Fetch existing class IDs for the dropdown
def fetch_classes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT class_id, class_name FROM class")
    classes = cursor.fetchall()
    conn.close()
    return classes


# Add student and parent to the database and capture face
def add_student_parent_and_capture_face(student_data, parent_data):
    global conn
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT student_id FROM students WHERE student_id = %s", (student_data[0],))
        existing_student = cursor.fetchone()

        if existing_student:
            st.error(f"❌ Student with ID {student_data[0]} already exists.")
            return

        # Insert student details
        student_sql = """
        INSERT INTO students (student_id, first_name, last_name, date_of_birth, parent_email, class_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(student_sql, student_data)

        # Insert parent details
        parent_sql = """
        INSERT INTO parent (parent_firstname, parent_lastname, email, phone_number, student_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(parent_sql, parent_data)

        conn.commit()

        # Convert student_id to string to avoid the type error
        student_id_str = str(student_data[0])

        # Start face capture for the student
        st.write("### Capturing Student's Face...")
        captured_faces_path = FaceCapture.run_capture_app(student_id_str)  # Pass student_id as string
        st.success("✅ Face capture completed.")
        return captured_faces_path

    except mysql.connector.Error as err:
        st.error(f"❌ Database Error: {err}")
    except Exception as e:
        st.error(f"❌ Face Capture Error: {str(e)}")
    finally:
        conn.close()


# Streamlit app
st.title("🌟 Face Recognition System 🌟")

st.write("#### This Face recognition system is created by Mohamed Riham HND student from BCAS Campus")
st.write("Add student and parent details in the left side bar, after that encode and train them by clicking the buttons. "
         "otherwise, Run the Recognizer to track the attendance of Students with the Camera.")


# Display the form in the sidebar
with st.sidebar:
    st.write("### Add Student and Parent Details")

    # Form for student and parent details
    with st.form("add_student_form"):
        st.write("#### Student Details")
        student_id = st.number_input("Student ID", min_value=1, step=1, format="%d")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        date_of_birth = st.date_input("Date of Birth")

        classes = fetch_classes()
        class_id = st.selectbox("Class", [("", "Select a class")] + [(cls[0], cls[1]) for cls in classes])

        st.write("#### Parent Details")
        parent_firstname = st.text_input("Parent First Name")
        parent_lastname = st.text_input("Parent Last Name")
        parent_email = st.text_input("Parent Email (Mandatory)")
        phone_number = st.text_input("Phone Number")

        submitted = st.form_submit_button("Submit")

        if submitted:
            if not all([student_id, first_name, last_name, parent_firstname, parent_lastname]):
                st.error("⚠️ Please fill in all required fields.")
            else:
                student_data = (
                    student_id,
                    first_name,
                    last_name,
                    date_of_birth.strftime('%Y-%m-%d'),
                    parent_email if parent_email else None,
                    class_id[0] if class_id else None
                )
                parent_data = (
                    parent_firstname,
                    parent_lastname,
                    parent_email if parent_email else None,
                    phone_number,
                    student_id
                )
                captured_faces_path = add_student_parent_and_capture_face(student_data, parent_data)


# Buttons for encoding, training, recognition
if st.button("2. Encode Faces"):
    st.write("### Starting Face Encoding...")
    if st.button("Stop Encoding"):
        quit()
    try:
        pre_processing.delete_images_without_faces('captured_faces')
        Encoding.start_encode()
        st.success("✅ Face encoding completed.")
    except Exception as e:
        st.error(f"❌ Error during face encoding: {str(e)}")

if st.button("3. Train Model"):
    st.write("### Training Model...")
    if st.button("Stop Training the model"):
        quit()
    try:
        train_encodings()
        st.success("✅ Model training completed.")
    except Exception as e:
        st.error(f"❌ Error during model training: {str(e)}")

if st.button("4. Recognize Faces"):
    st.write("### Starting Face Recognition...")
    video_placeholder = st.empty()  # Placeholder for video feed
    if st.button("Close"):
        quit()

    try:
        last_csv_update_time = time.time()  # Track the last time attendance was updated

        for frame in Recognizer.run_recognition():
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            video_placeholder.image(rgb_frame)

            # Check if it's time to update attendance
            if time.time() - last_csv_update_time >= 5:  # Every 5 seconds
                csv_filename = send_email.get_todays_csv_filename()
                send_email.insert_attendance_from_csv(csv_filename)
                last_csv_update_time = time.time()  # Update the timestamp

    except Exception as e:
        st.error(f"❌ Error during face recognition: {str(e)}")

if "selected_section" not in st.session_state:
    st.session_state.selected_section = None  # Initialize the selected section state

st.write("## 📋 Data Overview")

# Top-level buttons to select the section
if st.button("Show Student Details"):
    st.session_state.selected_section = "students"

if st.button("Show Parent Details"):
    st.session_state.selected_section = "parents"

if st.button("Show Class Details"):
    st.session_state.selected_section = "classes"

if st.button("Show Attendance Details"):
    st.session_state.selected_section = "attendance"

# Display the selected section
if st.session_state.selected_section == "students":
    st.write("### Student Details")
    try:
        student_df = fetch_students()
        st.dataframe(student_df)
    except Exception as e:
        st.error(f"❌ Error fetching student details: {str(e)}")

elif st.session_state.selected_section == "parents":
    st.write("### Parent Details")
    try:
        parent_df = fetch_parents()
        st.dataframe(parent_df)
    except Exception as e:
        st.error(f"❌ Error fetching parent details: {str(e)}")

elif st.session_state.selected_section == "classes":
    st.write("### Class Details")
    try:
        class_df = fetch_class_details()
        st.dataframe(class_df)
    except Exception as e:
        st.error(f"❌ Error fetching class details: {str(e)}")

elif st.session_state.selected_section == "attendance":
    st.write("### Attendance Details")
    try:
        attendance_df = fetch_attendance()
        st.dataframe(attendance_df)
    except Exception as e:
        st.error(f"❌ Error fetching attendance details: {str(e)}")

# Exit button
# if st.button("5. Exit"):
#     st.write("Exiting application...")
#     st.stop()  # Stops Streamlit app execution
