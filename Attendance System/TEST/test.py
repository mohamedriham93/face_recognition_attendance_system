from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import os
import face_recognition
import numpy as np
import pickle
import seaborn as sns
import matplotlib.pyplot as plt

# Load training data and label encoder
ENCODINGS_FILE = 'Files/face_encodings.pkl'
LABEL_ENCODER_FILE = 'Files/label_encoder.pkl'

with open(ENCODINGS_FILE, 'rb') as f:
    X_train, y_train = pickle.load(f)

with open(LABEL_ENCODER_FILE, 'rb') as f:
    label_encoder = pickle.load(f)

# Initialize variables for storing ground-truth and predictions
true_labels = []
predicted_labels = []

TEST_IMAGES_PATH = 'test_images'

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

                # Predict the label
                distances = np.linalg.norm(X_train - test_encoding, axis=1)
                closest_index = np.argmin(distances)
                predicted_label = y_train[closest_index]
                predicted_name = label_encoder.inverse_transform([predicted_label])[0]

                # Append ground-truth and prediction
                true_labels.append(student_id)  # Ground-truth from folder name
                predicted_labels.append(predicted_name)
            else:
                print(f"No face detected in {image_path}")

# Calculate metrics
accuracy = accuracy_score(true_labels, predicted_labels)
conf_matrix = confusion_matrix(true_labels, predicted_labels)
class_report = classification_report(true_labels, predicted_labels, target_names=label_encoder.classes_)

print(f"Accuracy: {accuracy * 100:.2f}%")
print("\nConfusion Matrix:\n", conf_matrix)
print("\nClassification Report:\n", class_report)

# Visualize the confusion matrix
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.show()
