from ultralytics import YOLO
import cv2

# Load your YOLO model (.pt file) and force CPU usage
model = YOLO("yolo12n.pt")   # example: "yolov12n.pt"
model.to('cpu')  # Force CPU usage due to incompatible GPU

width, height = 640, 640

# Open webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

while True:
    ret, frame = cap.read(0)
    if not ret:
        break

    # Run YOLO inference on CPU
    results = model(frame, device='cpu')[0]

    # Draw boxes manually using OpenCV
    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        label = f"{model.names[cls]} {conf:.2f}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(frame, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # Show frame
    cv2.imshow("YOLO Webcam", frame)

    # ESC to exit
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
