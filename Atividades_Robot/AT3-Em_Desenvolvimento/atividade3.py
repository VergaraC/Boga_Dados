import cv2
import matplotlib.pyplot as plt
import numpy as np
import math
import time

cap = cv2.VideoCapture("video1.mp4")
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, video = cap.read()

    rgb = cv2.cvtColor(video, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(video, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(video, cv2.COLOR_BGR2HSV)

    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

#    video_eq = cv2.equalizeHist(gray)

    ret, limiarizada = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY)

    lines = cv2.HoughLines(limiarizada,1, np.pi/180, 200)

    for line in lines:
        for rho,theta in line:
            m = np.cos(theta)
            b = np.sin(theta)
            
#            time.sleep(0.5)

            if 0.7 > m > 0.6 or -0.7 > m > -0.8:
                if m < 0:
                    print(m)
                x0 = m*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(m))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(m))
                cv2.line(video,(x1,y1),(x2,y2),(0,255,0),10)
            else:
                pass

    #lower_white = np.array([0, 0, 150])
    #higher_white = np.array([255, 30, 255])

    #mask = cv2.inRange(hsv, lower_white, higher_white)
    #cv2.imshow('threshold', video)
    cv2.imshow('video', video)
    #cv2.imshow('mask', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()