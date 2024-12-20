import os
import cv2
import face_recognition


def delete_images_without_faces(root_folder):
    for root, _, files in os.walk(root_folder):
        for file in files:
            file_path = os.path.join(root, file)

            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image = cv2.imread(file_path)

                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                face_locations = face_recognition.face_locations(rgb_image)

                if not face_locations:
                    print(f"No faces found in {file_path}. Deleting...")
                    os.remove(file_path)
                else:
                    print(f"Faces detected in {file_path}. Keeping the file.")


if __name__ == "__main__":
    delete_images_without_faces('captured_faces')


