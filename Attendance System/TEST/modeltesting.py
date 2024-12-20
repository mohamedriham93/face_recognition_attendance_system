import os
import face_recognition
import pickle
import numpy as np
from sklearn.metrics import classification_report

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

                    # Compare the test encoding with training encodings
                    distances = np.linalg.norm(X_train - test_encoding, axis=1)
                    closest_index = np.argmin(distances)
                    predicted_label = y_train[closest_index]

                    # Decode the predicted label
                    predicted_name = label_encoder.inverse_transform([predicted_label])[0]

                    # Compare with the actual label (folder name)
                    if predicted_name == student_id:
                        correct_predictions += 1
                    else:
                        incorrect_predictions += 1
                        print(f"Incorrect Prediction: Predicted {predicted_name}, Actual {student_id}")
                else:
                    print(f"No face detected in {image_path}")

    # Accuracy calculation
    accuracy = (correct_predictions / total_images) * 100 if total_images > 0 else 0
    print("\n--- Test Results ---")
    print(f"Total Test Images: {total_images}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Incorrect Predictions: {incorrect_predictions}")
    print(f"Accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    # Load the model and label encoder
    X_train, y_train, label_encoder = load_model_and_label_encoder()

    # Test the model
    test_model(X_train, y_train, label_encoder)
