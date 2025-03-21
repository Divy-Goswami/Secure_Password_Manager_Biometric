import cv2
import numpy as np

def verify_face(stored_embedding, captured_image):
    # Convert captured image to grayscale
    captured_image = cv2.imdecode(np.frombuffer(captured_image, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)

    # Detect face in the captured image
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(captured_image, scaleFactor=1.1, minNeighbors=5)

    if len(faces) == 0:
        return False  # No face detected

    # Extract the first face (assuming only one face is present)
    x, y, w, h = faces[0]
    face_roi = captured_image[y:y+h, x:x+w]

    # Resize the face ROI to match the stored embedding size
    resized_face = cv2.resize(face_roi, (128, 128))

    # Compare the resized face with the stored embedding
    similarity = np.linalg.norm(np.array(resized_face) - np.frombuffer(stored_embedding, dtype=np.uint8))
    return similarity < 100  # Threshold for similarity (adjust as needed)