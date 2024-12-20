import csv
import os
import datetime
from datetime import datetime
import time
import pymysql

# Database configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'facerecognition'

# CSV file configuration
CSV_FOLDER = "csv/."  # Assuming the CSV is in the current directory


def get_todays_csv_filename():
    """Generate the CSV filename for today's date."""
    today_date = datetime.now().strftime("%Y-%m-%d")
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


def insert_attendance_from_csv(csv_file_path):
    """Insert attendance data from a CSV file into the database."""
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

                    # Check if attendance has already been marked for this student on this date
                    if is_attendance_recorded(cursor, student_id, date):
                        print(f"⏭️ Attendance already recorded for Student ID {student_id} on {date}. Skipping...")
                        continue

                    # Insert the data into the attendance table
                    sql = """
                    INSERT INTO attendance (student_id, date, time, status)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql, (student_id, date, time, status))

                except KeyError as e:
                    print(f"❌ Missing expected CSV column: {e}")
                    continue
                except Exception as e:
                    print(f"❌ Error processing row {row}: {e}")
                    continue

        connection.commit()
        print(f"✅ Attendance data from {csv_file_path} inserted successfully.")

    except pymysql.MySQLError as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    while True:
        csv_filename = get_todays_csv_filename()
        insert_attendance_from_csv(csv_filename)

        # Wait for 20 seconds before the next execution
        print("⏳ Waiting for the next check...")
        time.sleep(5)