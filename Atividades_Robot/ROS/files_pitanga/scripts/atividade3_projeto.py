# -*- coding:utf-8 -*-
import cv2
import matplotlib.pyplot as plt
import numpy as np
import math
import time

coef_angular_positivo = []
coef_angular_negativo = []
coef_linear_positivo = []
coef_linear_negativo = []

mediana_x = 0
mediana_y = 0

def ponto_fuga(frame):
    lista_xi = []
    lista_yi = []

    x_ponto_fuga = []
    y_ponto_fuga = []

    avg_x=0
    avg_y=0

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    ret, limiarizada = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)

    lines = cv2.HoughLines(limiarizada,1, np.pi/180, 200)

    for line in lines:
        for rho,theta in line:
            m = np.cos(theta)
            b = np.sin(theta)
            
            if m > 0.4:
                coef_angular_positivo.append(m)
                coef_linear_positivo.append(b)
                x0 = m*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(m))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(m))
                line = cv2.line(frame,(x1,y1),(x2,y2),(0,255,0),3)
            
            elif m < -0.4:
                coef_angular_negativo.append(m)
                coef_linear_negativo.append(b)
                x0 = m*rho
                y0 = b*rho
                x3 = int(x0 + 1000*(-b))
                y3 = int(y0 + 1000*(m))
                x4 = int(x0 - 1000*(-b))
                y4 = int(y0 - 1000*(m))
                line = cv2.line(frame,(x3,y3),(x4,y4),(0,255,0),3)
                
                try:
                    h1 = coef_linear_positivo[len(coef_linear_positivo)-1]
                    m1 = coef_angular_positivo[len(coef_angular_positivo)-1]

                    h2 = coef_linear_negativo[len(coef_linear_negativo)-1]
                    m2 = coef_angular_negativo[len(coef_angular_negativo)-1]
                    
                    xi = ((x1*y2 - y1*x2)*(x3 - x4) - (x1-x2)*(x3*y4 - y3*x4))/((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))#((h2-h1)/(m1-m2))
                    yi = ((x1*y2 - y1*x2)*(y3 - y4) - (y1-y2)*(x3*y4 - y3*x4))/((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))#(m1*xi) + h1

                    lista_xi.append(xi)
                    lista_yi.append(yi)

                    x_ponto_fuga.append(xi)
                    y_ponto_fuga.append(yi)
                    
                except:
                    pass
            else:
                pass


    try:
        avg_x = int(np.mean(x_ponto_fuga))
        avg_y = int(np.mean(y_ponto_fuga))
        cv2.circle(frame, (avg_x,avg_y), 3, (255,0,0), 5)

    except:
        pass

    return (avg_x,avg_y)