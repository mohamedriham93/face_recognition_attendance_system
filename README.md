# Face Recognition Attendance System

## Introduction

The **Face Recognition Attendance System** is a project designed to automate attendance tracking using facial recognition. This system identifies and records student attendance in real-time, ensuring accurate records and providing instant email notifications to parents.

## Features

- Real-time face recognition using a camera.
- Attendance tracking and logging.
- Database storage with MySQL.
- Email notifications for parents.
- GUI-based application for ease of use.
- Support for handling unknown faces by labeling them as `unknown`.
- Secure storage of student and parent information.

## Technologies Used

- **Programming Language:** Python
- **Database:** MySQL
- **Libraries and Frameworks:**
  - `face_recognition`
  - `OpenCV`
  - `PyQt`/`PySide` for GUI
  - `smtplib` for email notifications

## Setup and Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/mohamedriham93/automated-attendance-system-using-face-recognition.git
   ```




4. Set up the MySQL database:

   - Create a database and tables using the provided SQL scripts in the `database` folder.
   - Update the database configuration in the `.env` file or relevant Python script.

5. Run the application:

   ```bash
   streamlit main-streamlit.py
   ```
   or u can click the run.bat instead
   

Usage

- **Capture Faces:**
  Use the GUI to capture student faces and encode them with unique index numbers.
- **Train the Model:**
  Train the recognition model using the encoded face data.
- **Recognize Faces:**
  Run the recognition module to record attendance in real-time.
- **View Attendance Records:**
  Check the local website for detailed attendance and schedules.

How It Works

1. Face Image Capture:

   - Capture images of students and store them in class-specific folders.
   - Generate face encodings while capturing and store them with labels.

2. Model Training:

   - Train a face recognition model using the stored encodings and labels.
   - Save the trained model in TFLite format for optimized performance.

3. Attendance Recognition:

   - Use the model to recognize faces in real-time.
   - Log attendance in the database and notify parents via email.

4. Data Storage:

   - Store student and parent details securely in the MySQL database.
   - Attendance records can be accessed through a local web interface.

Future Enhancements

- Add support for detecting multiple faces simultaneously.
- Implement advanced analytics on attendance data.
- Introduce mobile app integration for remote access.
- Enhance security with data encryption and multi-factor authentication.

Contributing

Contributions are welcome! Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.


