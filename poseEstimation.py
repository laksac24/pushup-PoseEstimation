import cv2
import mediapipe as mp

cap = cv2.VideoCapture("./Videos/Pushups.mp4")

# initialize mideapipe pose estimation model
mpPose = mp.solutions.pose
pose = mpPose.Pose()
mpDraw = mp.solutions.drawing_utils

while True:
    sucess, frame = cap.read()
    if sucess:
        rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgbFrame)
        # print(results.pose_landmarks)
        lmList = []
        if results.pose_landmarks:
            mpDraw.draw_landmarks(frame,results.pose_landmarks,mpPose.POSE_CONNECTIONS)
            for id,lm in enumerate(results.pose_landmarks.landmark):
                # print(id,lm)
                h, w, c = frame.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                lmList.append([id,cx,cy])
            cv2.circle(frame,(lmList[14][1],lmList[14][2]),15,(255,0,255), cv2.FILLED)
        cv2.imshow("output", frame)
        if cv2.waitKey(30) & 0xFF==ord('q') :
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()