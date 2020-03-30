# -*- coding:utf-8 -*-
import cv2
import matplotlib.pyplot as plt
import numpy as np
import math
import time

cap = cv2.VideoCapture("video1.mp4")
#cap = cv2.VideoCapture("video2.mp4")
#cap = cv2.VideoCapture("video3.mp4")
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

coef_angular_positivo = []
coef_angular_negativo = []
coef_linear_positivo = []
coef_linear_negativo = []

lista_xi = []
lista_yi = []

while True:
    ret, video = cap.read()

    rgb = cv2.cvtColor(video, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(video, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(video, cv2.COLOR_BGR2HSV)

    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

#    video_eq = cv2.equalizeHist(gray)

#====================================================================
    #threshold para o video 1:
    #ret, limiarizada = cv2.threshold(gray, 215, 255, cv2.THRESH_BINARY)

#====================================================================

#====================================================================
    #threshold para o video 2:
    #ret, limiarizada = cv2.threshold(gray,240,255,cv2.THRESH_BINARY)
#====================================================================

#====================================================================
    #threshold para o video 3:
    ret, limiarizada = cv2.threshold(gray,230,255,cv2.THRESH_BINARY)    
#====================================================================
    lines = cv2.HoughLines(limiarizada,1, np.pi/180, 200)

    for line in lines:
        for rho,theta in line:
            m = np.cos(theta)
            b = np.sin(theta)
            
#            time.sleep(0.5)

#====================================================================
# if para o video 1:
            if 0.7 > m > 0.6: #or -0.7 > m > -0.8:
                coef_angular_positivo.append(m)
                coef_linear_positivo.append(b)
                x0 = m*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(m))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(m))
                line = cv2.line(video,(x1,y1),(x2,y2),(0,255,0),3)
            
            elif -0.7 > m > -0.8:
                coef_angular_negativo.append(m)
                coef_linear_negativo.append(b)
                x0 = m*rho
                y0 = b*rho
                x3 = int(x0 + 1000*(-b))
                y3 = int(y0 + 1000*(m))
                x4 = int(x0 - 1000*(-b))
                y4 = int(y0 - 1000*(m))
                line = cv2.line(video,(x3,y3),(x4,y4),(0,255,0),3)
                try:
                    h1 = coef_linear_positivo[len(coef_linear_positivo)-1]
                    m1 = coef_angular_positivo[len(coef_angular_positivo)-1]

                    h2 = coef_linear_negativo[len(coef_linear_negativo)-1]
                    m2 = coef_angular_negativo[len(coef_angular_negativo)-1]
                    
                    xi = ((x1*y2 - y1*x2)*(x3 - x4) - (x1-x2)*(x3*y4 - y3*x4))/((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))#((h2-h1)/(m1-m2))
                    yi = ((x1*y2 - y1*x2)*(y3 - y4) - (y1-y2)*(x3*y4 - y3*x4))/((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))#(m1*xi) + h1

                    lista_xi.append(xi)
                    lista_yi.append(yi)

#                    termo_xi = int(np.round(len(lista_xi)/2))
#                    termo_yi = int(np.round(len(lista_yi)/2))

#                    print(termo_yi)
#                    print(termo_xi)
                    
#                    print(termo_xi)
#                    print(termo_yi)
#                    for i in lista_xi:
#                        print(lista_xi[int(np.mean(len(lista_xi)))])
#                    print(lista_xi[termo_xi])
#                    print(lista_yi[termo_yi])

#                    xi = lista_xi[termo_xi]
#                    yi = lista_yi[termo_yi]
#                    print(lista_xi[termo_xi])
#                    print(lista_yi[termo_yi])

#                    print(xi)
#                    print(yi)

                    ponto_fuga = cv2.circle(video, (xi,yi), 3, (0,0,255), 5)
#
                except:
                    pass
            else:
                pass

#====================================================================
# if para o video 2:
            #if 0.05 < m < 0.2 or -0.05> m > -0.2:    
            #    print(m)
            #    x0 = m*rho
            #    y0 = b*rho
            #    x1 = int(x0 + 1000*(-b))
            #    y1 = int(y0 + 1000*(m))
            #    x2 = int(x0 - 1000*(-b))
            #    y2 = int(y0 - 1000*(m))
            #    cv2.line(video,(x1,y1),(x2,y2),(0,255,0),10)
            #else:
            #    pass

#====================================================================

#================================== VIDEO 3 NAO ESTÁ DANDO MUITO CERTO (REVER) ==========================================

# if para o video 3:
            #if 0.6 < m < 0.7 or 0.75 < m < 0.78:
            #    print(m)
            #    x0 = m*rho
            #    y0 = b*rho
            #    x1 = int(x0 + 1000*(-b))
            #    y1 = int(y0 + 1000*(m))
            #    x2 = int(x0 - 1000*(-b))
            #    y2 = int(y0 - 1000*(m))
            #    cv2.line(video,(x1,y1),(x2,y2),(0,255,0),10)
            #else:
            #    pass

#    lower_white = np.array([0, 0, 150])
#    higher_white = np.array([255, 30, 255])

#    mask = cv2.inRange(hsv, lower_white, higher_white)
    #cv2.imshow('threshold', video)
    cv2.imshow('video', video)
#    cv2.imshow('mask', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()