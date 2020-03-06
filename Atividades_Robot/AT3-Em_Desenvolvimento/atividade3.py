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

    ret, limiarizada = cv2.threshold(gray, 190, 255, cv2.THRESH_BINARY)

    lines = cv2.HoughLines(limiarizada,1, np.pi/180, 200)

    for line in lines:
        for rho,theta in line:
            a = np.cos(theta)
            b = np.sin(theta)
            print(a)
#            time.sleep(0.5)
            if a > 0.5 or a < -0.5:
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a))
                cv2.line(video,(x1,y1),(x2,y2),(0,255,0),10)
            else:
                pass

#    a,b,c = lines.shape
#    for i in range(a):
#        rho1 = lines[0][0][0]
#        theta1 = lines[0][0][1]
#        rho2 = lines[1][0][0]
#        theta2 = lines[1][0][1]
        
#        a1 = math.cos(theta1)
#        b1 = math.sin(theta1)
#        x0, y0 = a1*rho1, b1*rho1
#        pt1 = (int(x0+1000*(-b1)), int(y0+1000*(a1)))
#        pt2 = (int(x0-1000*(-b1)), int(y0-1000*(a1)))
#        cv2.line(video, pt1, pt2, (0, 0, 255), 3, cv2.LINE_AA)

#        a2 = math.cos(theta2)
#        b2 = math.sin(theta2)
#        x0_2, y0_2 = a2*rho2, b2*rho2
#        pt2_1 = (int(x0_2+1000*(-b2)), int(y0_2+1000*(a2)))
#        pt2_2 = (int(x0_2-1000*(-b2)), int(y0_2-1000*(a2)))
#        cv2.line(video, pt2_1, pt2_2, (0, 0, 255), 3, cv2.LINE_AA)

#    try:
#        line1 = lines[0][0]    
#        theta1 = line1[1]
#        rho1 = line1[0]
#        a1 = np.cos(theta1)
#        b1 = np.sin(theta1)
#        x0_1 = a1*rho1
#        y0_1 = b1*rho1
#        x1_1 = int(x0_1 + 1000*(-b1))
#        y1_1 = int(y0_1 + 1000*(a1))
#        x2_1 = int(x0_1 - 1000*(-b1))
#        y2_1 = int(y0_1 - 1000*(a1))

#        cv2.line(video, (x1_1,y1_1), (x2_1,y2_1), (0,0,255), 3)
        
#    except:
#        pass
        
#    try:
#        line2 = lines[1][0]
#        rho2 =  line2[0]
#        theta2 = line2[1]
#       a2 = np.cos(theta2)
#       b2 = np.sin(theta2)
#        x0_2 = a2*rho2
#        y0_2 = b2*rho2
#        x1_2 = int(x0_2 + 1000*(-b2))
#       y1_2 = int(y0_2 + 1000*(a2))
#        x2_2 = int(x0_2 - 1000*(-b2))
#        y2_2 = int(y0_2 - 1000*(a2))

#        cv2.line(video, (x2_1,y2_1), (x2_2,y2_2), (0,255,0), 3)
        
#    except:
#        pass
        #cv2.line(video,(x1,y1),(x2,y2),(0,0,255),2)
 
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