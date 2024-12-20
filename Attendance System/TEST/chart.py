import os
import face_recognition
import pickle
import numpy as np
import time
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt

# Configuration
TEST_IMAGES_PATH = "test_images"
ENCODINGS_FILE = 'Files/face_encodings.pkl'
LABEL_ENCODER_FILE = 'Files/label_encoder.pkl'

def load_model_and_label_encoder():
    """Load the encodings and label encoder from the saved files."""
    with open(ENCODINGS_FILE, 'rb') as f:
        X, y = pickle.load(f)
    with open(LABEL_ENCODER_FILE, 'rb') as f:
        label_encoder = pickle.load(f)
    return X, y, label_encoder

def test_model(X_train, y_train, label_encoder):
    """Test the model on images from the test dataset."""
    # Initialize counters for evaluation
    total_images = 0
    correct_predictions = 0
    incorrect_predictions = 0
    false_positives = 0
    false_negatives = 0
    confidence_levels = []

    total_time = 0  # Initialize time variable

    # Iterate through each folder in the test images path
    for student_id in os.listdir(TEST_IMAGES_PATH):
        student_folder = os.path.join(TEST_IMAGES_PATH, student_id)
        if os.path.isdir(student_folder):  # Ensure it's a folder
            for image_file in os.listdir(student_folder):
                image_path = os.path.join(student_folder, image_file)
                test_image = face_recognition.load_image_file(image_path)

                # Get face encodings for the test image
                test_encodings = face_recognition.face_encodings(test_image)
                if len(test_encodings) > 0:
                    test_encoding = test_encodings[0]
                    total_images += 1

                    # Start time measurement for processing speed
                    start_time = time.time()

                    # Compare the test encoding with training encodings
                    distances = np.linalg.norm(X_train - test_encoding, axis=1)
                    closest_index = np.argmin(distances)
                    predicted_label = y_train[closest_index]

                    # Calculate confidence as inverse of distance (higher distance means lower confidence)
                    confidence = 1 / (distances[closest_index] + 1e-6)  # Add a small value to avoid division by zero
                    confidence_levels.append(confidence)

                    # Decode the predicted label
                    predicted_name = label_encoder.inverse_transform([predicted_label])[0]

                    # Stop time measurement for processing speed
                    end_time = time.time()
                    total_time += (end_time - start_time)  # Accumulate processing time

                    # Compare with the actual label (folder name)
                    if predicted_name == student_id:
                        correct_predictions += 1
                    else:
                        incorrect_predictions += 1
                        print(f"Incorrect Prediction: Predicted {predicted_name}, Actual {student_id}")
                        if predicted_name != "Unknown":
                            false_positives += 1
                        else:
                            false_negatives += 1
                else:
                    print(f"No face detected in {image_path}")
                    false_negatives += 1  # If no face is detected, it's a false negative

    # Accuracy calculation
    accuracy = (correct_predictions / total_images) * 100 if total_images > 0 else 0
    avg_processing_speed = total_time / total_images if total_images > 0 else 0
    print("\n--- Test Results ---")
    print(f"Total Test Images: {total_images}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Incorrect Predictions: {incorrect_predictions}")
    print(f"False Positives: {false_positives}")
    print(f"False Negatives: {false_negatives}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Average Processing Speed: {avg_processing_speed:.4f} seconds/image")

    # Visualization of results (confidence chart and predictions)
    # Line Chart: Confidence Levels
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(confidence_levels)), confidence_levels, label='Confidence Levels', color='blue', marker='s')

    plt.xlabel('Test Cases')
    plt.ylabel('Confidence Level (%)')
    plt.title('Confidence Levels of Predictions')
    plt.grid(True)
    plt.show()

    # Bar Chart: Correct vs Incorrect Predictions
    labels = ['Correct', 'Incorrect']
    prediction_counts = [correct_predictions, incorrect_predictions]

    plt.figure(figsize=(8, 6))
    plt.bar(labels, prediction_counts, color=['green', 'red'])
    plt.xlabel('Prediction Outcome')
    plt.ylabel('Count')
    plt.title('Prediction Accuracy')
    plt.show()

if __name__ == "__main__":
    # Load the model and label encoder
    X_train, y_train, label_encoder = load_model_and_label_encoder()

    # Test the model
    test_model(X_train, y_train, label_encoder)
