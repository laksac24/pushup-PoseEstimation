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

# # Store session data in a dictionary
# sessions = {}

# @app.post("/upload")
# async def upload_frame(file: UploadFile = File(...), session_id: str = "default"):
#     """Process the uploaded frame and count push-ups for a session."""
#     if session_id not in sessions:
#         sessions[session_id] = {"dir": 0, "count": 0, "last_change_time": time.time(), "active": True}

#     session = sessions[session_id]

#     if not session["active"]:
#         return {"message": "Session ended", "final_pushup_count": int(floor(session["count"]))}

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
#                 per = np.interp(angle, (70, 145), (0, 100))
#                 if per == 0 and session["dir"] == 0:
#                     session["count"] += 0.5
#                     session["dir"] = 1
#                 if per == 100 and session["dir"] == 1:
#                     session["count"] += 0.5
#                     session["dir"] = 0

#     # If count changes, reset inactivity timer
#     if session["count"] != int(floor(session["count"])):
#         session["last_change_time"] = time.time()

#     # If no activity for 10 seconds, end session
#     if time.time() - session["last_change_time"] > 10:
#         session["active"] = False
#         return {"message": "No activity detected for 10 seconds", "final_pushup_count": int(floor(session["count"]))}

#     return {"pushup_count": int(floor(session["count"]))}

# @app.get("/")
# def home():
#     return {"message": "Push-up counter API is running!"}



# from flask import Flask, render_template, Response, request, jsonify
# import cv2
# import numpy as np
# import base64
# import time
# from math import floor
# import poseestimationmodule as pm  # Ensure pose estimation module is imported

# app = Flask(__name__)

# detector = pm.poseDetector()
# dir = 0
# count = 0
# last_change_time = time.time()
# last_count = count

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/process_video', methods=['POST'])
# def process_video():
#     global count, dir, last_change_time, last_count

#     # Receive the frame from the frontend
#     data = request.json['frame']
#     img_data = base64.b64decode(data.split(',')[1])  # Decode base64 frame
#     np_arr = np.frombuffer(img_data, np.uint8)
#     frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

#     # Process frame with pose estimation (Draw Only One Detection)
#     frame = detector.findPose(frame, draw=False)
#     lmList = detector.findPosition(frame, draw=False)

#     if len(lmList) != 0:
#         # Find a single relevant angle (Modify the points if necessary)
#         angle = detector.findAngle(frame, 12, 14, 16, draw=True)  # Draw only one angle
        
#         # Process movement count based on the angle
#         if angle:
#             per = np.interp(angle, (70, 145), (0, 100))
#             if per == 0 and dir == 0:
#                 count += 0.5
#                 dir = 1
#             if per == 100 and dir == 1:
#                 count += 0.5
#                 dir = 0

#     # Reset inactivity timer if count changes
#     if count != last_count:
#         last_change_time = time.time()
#         last_count = count

#     # Auto-reset count if no movement for 10 seconds
#     if time.time() - last_change_time > 10:
#         count = 0  # Reset count

#     # Convert processed frame back to base64 for frontend display
#     _, buffer = cv2.imencode('.jpg', frame)
#     processed_frame = base64.b64encode(buffer).decode('utf-8')

#     return jsonify({'frame': f'data:image/jpeg;base64,{processed_frame}', 'count': int(floor(count))})

# if __name__ == '__main__':
#     app.run(debug=True)



# import cv2
# import numpy as np
# import base64
# from fastapi import FastAPI, File, UploadFile
# from pydantic import BaseModel
# import poseestimationmodule as pm
# from math import floor
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# # Allow frontend access
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# detector = pm.poseDetector()
# dir = 0
# count = 0

# class ImageData(BaseModel):
#     image: str  # Base64 encoded image

# @app.post("/process_frame/")
# async def process_frame(data: ImageData):
#     global count, dir

#     # Decode base64 image
#     image_bytes = base64.b64decode(data.image)
#     nparr = np.frombuffer(image_bytes, np.uint8)
#     frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#     frame = detector.findPose(frame, draw=False)
#     lmList = detector.findPosition(frame, draw=False)

#     if len(lmList) != 0:
#         angle = detector.findAngle(frame, 12, 14, 16, draw=True)
#         angle2 = detector.findAngle(frame, 12, 24, 28, draw=True)
#         detector.findAngle(frame, 24, 36, 28, draw=True)

#         if angle2:
#             if 160 < angle2 < 190:
#                 per = np.interp(angle, (70, 145), (0, 100))
#                 if per == 0 and dir == 0:
#                     count += 0.5
#                     dir = 1
#                 elif per == 100 and dir == 1:
#                     count += 0.5
#                     dir = 0

#     # Encode processed frame back to base64
#     _, buffer = cv2.imencode('.jpg', frame)
#     frame_base64 = base64.b64encode(buffer).decode("utf-8")

#     return {"count": int(floor(count)), "frame": frame_base64}




import cv2
import numpy as np
import base64
from fastapi import FastAPI
from pydantic import BaseModel
import poseestimationmodule as pm
from math import floor
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = pm.poseDetector()
dir = 0
count = 0
last_change_time = time.time()  # Timer for inactivity check
last_count = 0  # To track count changes

class ImageData(BaseModel):
    image: str  # Base64 encoded image

@app.post("/process_frame/")
async def process_frame(data: ImageData):
    global count, dir, last_change_time, last_count

    # Decode base64 image
    image_bytes = base64.b64decode(data.image)
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    frame = detector.findPose(frame, draw=False)
    lmList = detector.findPosition(frame, draw=False)

    if len(lmList) != 0:
        angle = detector.findAngle(frame, 12, 14, 16, draw=True)
        angle2 = detector.findAngle(frame, 12, 24, 28, draw=True)
        detector.findAngle(frame, 24, 36, 28, draw=True)

        if angle2:
            if 160 < angle2 < 190:
                per = np.interp(angle, (70, 145), (0, 100))
                if per == 0 and dir == 0:
                    count += 0.5
                    dir = 1
                elif per == 100 and dir == 1:
                    count += 0.5
                    dir = 0

    # Check inactivity (no change in count for 10 seconds)
    if count > 0 and count != last_count:
        last_change_time = time.time()  # Reset timer **only if count has started updating**
        last_count = count  # Update last count

    # 🛠 **Fix: Ensure session doesn't end immediately**
    if count > 0 and (time.time() - last_change_time > 10):
        return {"count": int(floor(count)), "final": True} # Indicate session end

    # Encode processed frame back to base64
    _, buffer = cv2.imencode('.jpg', frame)
    frame_base64 = base64.b64encode(buffer).decode("utf-8")

    return {"count": int(floor(count)), "frame": frame_base64, "final": False}

@app.post("/reset_session/")
async def reset_session():
    global count, dir, last_change_time, last_count

    # Reset all variables
    count = 0
    dir = 0
    last_change_time = time.time()
    last_count = 0

    return {"message": "Session reset successfully"}
