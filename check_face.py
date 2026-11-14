import cv2
import face_recognition

print("face_recognition imported OK")

cap = cv2.VideoCapture(0)
ok, frame = cap.read()
cap.release()
print("Webcam OK" if ok else "Webcam NOT detected")

if ok:
    rgb = frame[:, :, ::-1]  # OpenCV uses BGR, face_recognition uses RGB
    faces = face_recognition.face_locations(rgb)
    print(f"Faces found in the frame: {len(faces)}")