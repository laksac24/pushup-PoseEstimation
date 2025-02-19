from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
import cv2
import poseestimationmodule as pm
import numpy as np
from math import floor
import time
import threading

app = FastAPI()
cap = cv2.VideoCapture(0)
detector = pm.poseDetector()
dir = 0
count = 0
final_count = ''
streaming = False
processing_thread = None

frame_lock = threading.Lock()
current_frame = None


def process_video():
    global count, dir, final_count, streaming, current_frame

    # Countdown before starting detection
    start_time = time.time()
    while time.time() - start_time < 10:
        ret, frame = cap.read()
        if not ret or not streaming:
            return
        elapsed_time = int(time.time() - start_time)
        remaining_time = 10 - elapsed_time
        cv2.putText(frame, f"Starting in {remaining_time} sec", (220, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255),
                    2)
        with frame_lock:
            current_frame = frame
        time.sleep(1)

    # Start push-up detection
    last_change_time = time.time()
    last_count = count
    while streaming:
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

        if count != last_count:
            last_change_time = time.time()
            last_count = count

        if time.time() - last_change_time > 10:
            print("No activity detected for 10 seconds. Exiting...")
            break

        final_count = str(int(floor(count)))
        cv2.putText(frame, final_count, (300, 50), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 0), 2)
        with frame_lock:
            current_frame = frame
        time.sleep(0.05)


@app.get("/start")
def start_detection():
    global streaming, processing_thread
    if not streaming:
        streaming = True
        processing_thread = threading.Thread(target=process_video, daemon=True)
        processing_thread.start()
    return {"message": "Push-up detection started"}


def generate_frames():
    while True:
        with frame_lock:
            if current_frame is None:
                continue
            success, buffer = cv2.imencode('.jpg', current_frame)
            if not success:
                continue
            frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.websocket("/pushup_count")
async def pushup_count(websocket: WebSocket):
    await websocket.accept()
    global final_count
    while streaming:
        await websocket.send_text(final_count)
        time.sleep(1)
    await websocket.send_text("Final Count: " + final_count)
    await websocket.close()


@app.get("/stop")
def stop():
    global streaming
    streaming = False
    return {"message": "Detection stopped", "final_count": final_count}

