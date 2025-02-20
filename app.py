# from fastapi import FastAPI, File, UploadFile
# import cv2
# import numpy as np
# import poseestimationmodule as pm
# from fastapi.middleware.cors import CORSMiddleware
# from math import floor
# import time

# app = FastAPI()

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Change this for security
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize pose detector
# detector = pm.poseDetector()
# dir = 0
# count = 0
# last_change_time = time.time()
# active = True  # Flag to check if session is active

# @app.post("/upload")
# async def upload_frame(file: UploadFile = File(...)):
#     global dir, count, last_change_time, active

#     if not active:
#         return {"message": "Session ended", "final_pushup_count": int(floor(count))}

#     # Read image bytes and convert to OpenCV format
#     contents = await file.read()
#     nparr = np.frombuffer(contents, np.uint8)
#     frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#     if frame is None:
#         return {"error": "Invalid image"}

#     frame = detector.findPose(frame, draw=False)
#     lmList = detector.findPosition(frame, draw=False)

#     if len(lmList) != 0:
#         angle = detector.findAngle(frame, 12, 14, 16, draw=True)
#         angle2 = detector.findAngle(frame, 12, 24, 28, draw=True)

#         if angle2:
#             if 160 < angle2 < 190:
#                 per = np.interp(angle, (70, 115), (0, 100))
#                 if per == 0 and dir == 0:
#                     count += 0.5
#                     dir = 1
#                 if per == 100 and dir == 1:
#                     count += 0.5
#                     dir = 0

#     # If count changes, reset inactivity timer
#     if count != int(floor(count)):
#         last_change_time = time.time()

#     # If no activity for 10 seconds, end session
#     if time.time() - last_change_time > 10:
#         active = False
#         return {"message": "No activity detected for 10 seconds", "final_pushup_count": int(floor(count))}

#     return {"pushup_count": int(floor(count))}

# @app.get("/")
# def home():
#     return {"message": "Push-up counter API is running!"}



from fastapi import FastAPI, File, UploadFile
import cv2
import numpy as np
import poseestimationmodule as pm
from fastapi.middleware.cors import CORSMiddleware
from math import floor
import time

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pose detector
detector = pm.poseDetector()

# Store session data in a dictionary
sessions = {}

@app.post("/upload")
async def upload_frame(file: UploadFile = File(...), session_id: str = "default"):
    """Process the uploaded frame and count push-ups for a session."""
    if session_id not in sessions:
        sessions[session_id] = {"dir": 0, "count": 0, "last_change_time": time.time(), "active": True}

    session = sessions[session_id]

    if not session["active"]:
        return {"message": "Session ended", "final_pushup_count": int(floor(session["count"]))}

    # Read image bytes and convert to OpenCV format
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        return {"error": "Invalid image"}

    frame = detector.findPose(frame, draw=False)
    lmList = detector.findPosition(frame, draw=False)

    if len(lmList) != 0:
        angle = detector.findAngle(frame, 12, 14, 16, draw=True)
        angle2 = detector.findAngle(frame, 12, 24, 28, draw=True)

        if angle2:
            if 160 < angle2 < 190:
                per = np.interp(angle, (90, 150), (0, 100))
                if per == 0 and session["dir"] == 0:
                    session["count"] += 0.5
                    session["dir"] = 1
                if per == 100 and session["dir"] == 1:
                    session["count"] += 0.5
                    session["dir"] = 0

    # If count changes, reset inactivity timer
    if session["count"] != int(floor(session["count"])):
        session["last_change_time"] = time.time()

    # If no activity for 10 seconds, end session
    if time.time() - session["last_change_time"] > 10:
        session["active"] = False
        return {"message": "No activity detected for 10 seconds", "final_pushup_count": int(floor(session["count"]))}

    return {"pushup_count": int(floor(session["count"]))}

@app.get("/")
def home():
    return {"message": "Push-up counter API is running!"}
