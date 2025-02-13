import cv2
import poseestimationmodule as pm

cap = cv2.VideoCapture("./Videos/Pushups.mp4")
# cap = cv2.VideoCapture(0)
detector = pm.poseDetector()
while True:
    sucess, frame = cap.read()
    if sucess:
        frame = detector.findPose(frame)
        lmList = detector.findPosition(frame)
        print(lmList)
        cv2.imshow("output", frame)
        if cv2.waitKey(20) & 0xFF==ord('q'):
            break

    else:
        break