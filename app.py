from fastapi import FastAPI
import cv2
import poseestimationmodule as pm
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from math import floor
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domains for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/start")
def start_pushup_counter():
    final_count = ''
    cap = cv2.VideoCapture(0)
    detector = pm.poseDetector()
    dir = 0
    count = 0

    # Display a countdown before starting detection
    start_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            return {"error": "Camera not found"}

        elapsed_time = int(time.time() - start_time)
        remaining_time = 10 - elapsed_time

        if elapsed_time < 10:
            # Display countdown text in red
            text = f"Starting in {remaining_time} sec"
            cv2.putText(frame, text, (220, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            # Draw progress bar
            bar_x, bar_y, bar_width, bar_height = 100, 460, 400, 20
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (200, 200, 200), 2)

            fill_width = int((elapsed_time / 10) * bar_width)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), (0, 255, 0), -1)

            cv2.imshow("Pushup Counter", frame)
            if cv2.waitKey(50) & 0xFF == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                return {"message": "User exited before starting"}

            continue  # Skip detection until countdown ends

        break  # Exit countdown loop and start detection

    # Initialize timer for inactivity detection
    last_change_time = time.time()
    last_count = count

    while True:
        success, frame = cap.read()
        if success:
            frame = detector.findPose(frame, draw=False)
            lmList = detector.findPosition(frame, draw=False)

            if len(lmList) != 0:
                angle = detector.findAngle(frame, 12, 14, 16, draw=True)
                angle2 = detector.findAngle(frame, 12, 24, 28, draw=True)
                detector.findAngle(frame, 24, 36, 28, draw=True)

                if angle2:
                    if 160 < angle2 < 190:
                        per = np.interp(angle, (70, 115), (0, 100))
                        if per == 0 and dir == 0:
                            count += 0.5
                            dir = 1
                        if per == 100 and dir == 1:
                            count += 0.5
                            dir = 0

            # If count changes, reset inactivity timer
            if count != last_count:
                last_change_time = time.time()
                last_count = count

            # Auto-close if no count change for 10 seconds
            if time.time() - last_change_time > 10:
                break

            text = str(int(floor(count)))
            cv2.putText(frame, text, (300, 50), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 0), 2)

            final_count = text
            cv2.imshow("Pushup Counter", frame)
            if cv2.waitKey(50) & 0xFF == ord('q'):
                break
        else:
            break

    cap.release()
    cv2.destroyAllWindows()
    return {"pushup_count": final_count}
