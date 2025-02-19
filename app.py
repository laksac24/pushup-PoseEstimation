from fastapi import FastAPI
import cv2
import poseestimationmodule as pm
import numpy as np
from math import floor
import time
import threading

app = FastAPI()

# Global variable to store final count
final_count = 0

def pose_detection():
    global final_count

    cap = cv2.VideoCapture(0)
    detector = pm.poseDetector()
    dir = 0
    count = 0

    # 10-second Countdown Before Starting Detection
    start_time = time.time()
    while time.time() - start_time < 10:
        ret, frame = cap.read()
        if not ret:
            break

        elapsed_time = int(time.time() - start_time)
        remaining_time = 10 - elapsed_time

        # Display Countdown Text
        text = f"Starting in {remaining_time} sec"
        cv2.putText(frame, text, (220, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Draw Progress Bar at the Bottom
        bar_x, bar_y, bar_width, bar_height = 100, 460, 400, 20
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (200, 200, 200), 2)
        fill_width = int((elapsed_time / 10) * bar_width)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), (0, 255, 0), -1)

        cv2.imshow("Pose Detection", frame)
        if cv2.waitKey(50) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return

    # Pose Detection with Real-Time Display
    last_change_time = time.time()
    last_count = count

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = detector.findPose(frame, draw=False)
        lmList = detector.findPosition(frame, draw=False)

        if len(lmList) != 0:
            angle = detector.findAngle(frame, 12, 14, 16, draw=True)
            angle2 = detector.findAngle(frame, 12, 24, 28, draw=True)
            detector.findAngle(frame, 24, 36, 28, draw=True)

            if angle2 and 160 < angle2 < 190:
                per = np.interp(angle, (70, 115), (0, 100))
                if per == 0 and dir == 0:
                    count += 0.5
                    dir = 1
                if per == 100 and dir == 1:
                    count += 0.5
                    dir = 0

        # Reset inactivity timer if count changes
        if count != last_count:
            last_change_time = time.time()
            last_count = count

        # Exit if no change in 10 seconds
        if time.time() - last_change_time > 10:
            print("No movement detected for 10 seconds. Exiting...")
            break

        # Display Count on Screen
        text = str(int(floor(count)))
        cv2.putText(frame, text, (300, 50), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 0), 2)

        cv2.imshow("Pose Detection", frame)
        if cv2.waitKey(50) & 0xFF == ord('q'):
            break

    final_count = int(floor(count))  # Store Final Count
    cap.release()
    cv2.destroyAllWindows()


@app.get("/")
def home():
    return {"message": "Pose Detection API is running!"}


@app.get("/start")
def start_detection():
    detection_thread = threading.Thread(target=pose_detection)
    detection_thread.start()
    detection_thread.join()  # Wait for completion
    return {"final_count": final_count}
