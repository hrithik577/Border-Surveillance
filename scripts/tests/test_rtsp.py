import cv2

RTSP_URL = "rtsp://127.0.0.1:8554/border"

cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

if not cap.isOpened():
    raise RuntimeError("Could not connect to RTSP stream")

print("Connected to IBVAP RTSP stream.")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to read frame.")
        break

    cv2.imshow("IBVAP - Simulated CCTV", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
