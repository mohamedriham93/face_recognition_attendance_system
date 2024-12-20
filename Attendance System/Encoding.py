import os
# import cv2
import face_recognition
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder

# Configuration
DATASET_PATH = "captured_faces"
ENCODINGS_FILE = 'Files/face_encodings.pkl'
LABEL_ENCODER_FILE = 'Files/label_encoder.pkl'

def encode_faces(images_folder):
    face_encodings = {}
    for person_name in os.listdir(images_folder):
        person_folder = os.path.join(images_folder, person_name)
        person_encodings = []

        for image_file in os.listdir(person_folder):
            image_path = os.path.join(person_folder, image_file)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                person_encodings.append(encodings[0])

        if person_encodings:
            face_encodings[person_name] = person_encodings
    return face_encodings

def prepare_data_for_training(face_encodings):
    X, y = [], []
    for label, encodings in face_encodings.items():
        X.extend(encodings)
        y.extend([label] * len(encodings))

    return np.array(X), np.array(y)


def start_encode():
    print("Processing Feature Extraction... Please wait!")
    face_encodings = encode_faces(DATASET_PATH)
    X, y = prepare_data_for_training(face_encodings)

    le = LabelEncoder()
    y = le.fit_transform(y)

    with open(ENCODINGS_FILE, 'wb') as f:
        pickle.dump((X, y), f)
    with open(LABEL_ENCODER_FILE, 'wb') as f:
        pickle.dump(le, f)

    return print("Feature extraction complete! Encodings and label encoder have been saved.")


if __name__ == "__main__":
    start_encode()
