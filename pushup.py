import cv2
import poseestimationmodule as pm
import numpy as np
from math import floor

# cap = cv2.VideoCapture("Videos/Pushups.mp4")
cap = cv2.VideoCapture(0)
detector = pm.poseDetector()
dir = 0
count = 0
while True:
    sucess, frame= cap.read()
    if sucess:
        frame = detector.findPose(frame, draw = False)
        lmList = detector.findPosition(frame, draw=False)
        # print(lmList)
        if len(lmList)!=0:
            angle = detector.findAngle(frame, 12, 14, 16, draw=True)
            angle2 = detector.findAngle(frame, 12, 24, 28, draw=True)
            # detector.findAngle(frame, 24, 36, 28, draw=True)
            # print(angle)
            # print(angle2)
            if angle2:
                if angle2 > 160 and angle2 < 190:
                    per = np.interp(angle, (70,115), (0,100))
                    if per == 0:
                        if dir == 0:
                            count += 0.5
                            dir = 1
                    if per == 100:
                        if dir == 1:
                            count += 0.5
                            dir = 0
        text = str(int(floor(count)))
        cv2.putText(frame,text,(300,50),cv2.FONT_HERSHEY_DUPLEX,2,(0,0,0),2)
        print(text)
        cv2.imshow("output", frame)
        if cv2.waitKey(50) & 0xFF==ord('q'):
            break
    else:
        break