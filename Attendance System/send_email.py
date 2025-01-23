import csv
import os
import datetime
import pymysql
import smtplib
from smtplib import SMTPAuthenticationError, SMTPConnectError, SMTPException
import time

# Database configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'facerecognition'

# CSV file configuration
CSV_FOLDER = "csv/."  # Assuming the CSV is in the current directory

# Email configuration
SMTP_HOST = "smtp-mail.outlook.com"
SMTP_PORT = 587
FROM_EMAIL = "" # outlook email
EMAIL_PASSWORD = ""  # password


def get_todays_csv_filename():
    """Generate the CSV filename for today's date."""
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    return os.path.join(CSV_FOLDER, f"{today_date}.csv")


def is_attendance_recorded(cursor, student_id, date):
    """Check if attendance has already been marked for the student on the given date."""
    sql = """
    SELECT COUNT(*) FROM attendance
    WHERE student_id = %s AND date = %s
    """
    cursor.execute(sql, (student_id, date))
    count = cursor.fetchone()[0]
    return count > 0


def get_student_parent_email(cursor, student_id):
    """Retrieve the parent's email and student name for the given student ID."""
    sql = """
    SELECT CONCAT(first_name, ' ', last_name) AS student_name, parent_email
    FROM students 
    WHERE student_id = %s
    """
    cursor.execute(sql, (student_id,))
    result = cursor.fetchone()
    if result:
        student_name, parent_email = result
        # Ensure that the email is not empty or incorrectly formatted
        if parent_email and '@' in parent_email:
            return student_name, parent_email
        else:
            print(f"[!] Invalid email address for Student ID {student_id}: {parent_email}")
            return None, None
    return None, None

def send_email(to_email, student_name):
    """Send an email to the parent's email address."""
    message = f"""\
Subject: Attendance Notification

Dear Parent,

This is to inform you that your child, {student_name}, attended school today at {time.ctime()}.

Thanks,
School Administration
"""
    try:
        smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(FROM_EMAIL, EMAIL_PASSWORD)
        smtp.sendmail(FROM_EMAIL, to_email, message)
        smtp.quit()
        print(f"✅ Email sent to {to_email} for student {student_name}.")
    except SMTPAuthenticationError:
        print(f"[!] Authentication Error: Unable to send email to {to_email}. Check email credentials.")
    except SMTPConnectError:
        print(f"[!] Connection Error: Unable to connect to the SMTP server.")
    except SMTPException as e:
        print(f"[!] SMTP Error while sending email to {to_email}: {e}")
    except Exception as e:
        print(f"[!] Error sending email to {to_email}: {e}")


def insert_attendance_from_csv(csv_file_path):
    """Insert attendance data from a CSV file into the database and notify parents."""
    if not os.path.exists(csv_file_path):
        print(f"❌ CSV file not found: {csv_file_path}")
        return

    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor()

        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    student_id = int(row["Student ID"])
                    date = row["Date"]
                    time = row["Time"]
                    status = row["Status"].lower()  # Assuming status is case-insensitive

                    print(f"Processing record: Student ID {student_id}, Date {date}, Time {time}, Status {status}")

                    # Check if attendance has already been recorded
                    if is_attendance_recorded(cursor, student_id, date):
                        print(f"⏭️ Attendance already recorded for Student ID {student_id} on {date}. Skipping...")
                        continue

                    # Insert the data into the attendance table
                    sql = """
                    INSERT INTO attendance (student_id, date, time, status)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql, (student_id, date, time, status))
                    connection.commit()

                    # Get parent's email and student name
                    student_name, parent_email = get_student_parent_email(cursor, student_id)

                    if parent_email:
                        print(f"Sending email to {parent_email} for student {student_name}.")
                        send_email(parent_email, student_name)
                    else:
                        print(f"[!] Parent email not found for Student ID {student_id}.")

                except KeyError as e:
                    print(f"❌ Missing expected CSV column: {e}")
                    continue
                except Exception as e:
                    print(f"❌ Error processing row {row}: {e}")
                    continue

    except pymysql.MySQLError as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        connection.close()


if __name__ == "__main__":
    csv_filename = get_todays_csv_filename()
    insert_attendance_from_csv(csv_filename)

    # Wait for 5 seconds before the next execution
    print("⏳ Waiting for the next check...")
