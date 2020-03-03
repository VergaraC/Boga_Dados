# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

#Integrantes:
    # - Antonio Fuziy;
    # - Victor Vergara;
    # - André Rocco.

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# ==============================================================================================================================================

# CASO TENHA PROBLEMAS NA EXECUÇÃO COM AS TRÊS JANELAS, COMENTE AS LINHAS DE 107 A 117 PARA VISUALIZAR O PREENCHIMENTO E OS CONTORNOS DO CÍRCULO
# PARA VISUALIZAR O BRISK, DESCOMENTE AS LINHAS CITADAS ACIMA E COMENTE AS LINHAS 167 A 168.

# ==============================================================================================================================================

import cv2
import numpy as np
from time import sleep
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from math import pi
import math

brisk = cv2.BRISK_create()

bf = cv2.BFMatcher(cv2.NORM_HAMMING)

MINIMO_SEMELHANCAS = 7

def find_good_matches(descriptor_image1, frame_gray):

    des1 = descriptor_image1
    try:
        kp2, des2 = brisk.detectAndCompute(frame_gray,None)
    except:
        kp2=0
        des2=0

    matches = bf.knnMatch(des1,des2,k=2)

    good = []
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)

    return kp2, good

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

original_rgb = cv2.imread('insper.png')
img_original = cv2.cvtColor(original_rgb, cv2.COLOR_BGR2GRAY)

kp1, des1 = brisk.detectAndCompute(img_original ,None)

while True:
    ret, frame = cap.read()

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    lower_blue = np.array([137,103,91])
    higher_blue = np.array([179,255,255])
    lower_red = np.array([95,103,91])
    higher_red = np.array([179,255,255])

    mask = cv2.inRange(hsv, lower_blue, higher_blue)
    mask2 = cv2.inRange(hsv, lower_red, higher_red)

    image = cv2.bitwise_or(mask,mask2)

    circles = []
    circles = None

    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,2,40,param1=50,param2=100,minRadius=10,maxRadius=50)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        circles = circles[0]

        for i in circles:
            cv2.circle(bgr, (i[0],i[1]), i[2], (0,255,0), 2)

            cv2.circle(bgr, (i[0], i[1]), 2, (0,0,255), 3)

        if len(circles) > 1:
            circulo1 = circles[0]
            circulo2 = circles[1]
        else:
            circulo1 = circles[0]
            circulo2 = circulo1

        try:
            cv2.line(bgr, (circulo1[0], circulo1[1]), (circulo2[0], circulo2[1]), (0,0,255), 3)

        except:
            pass
    else:
        circulo1 = [1,1]
        circulo2 = [2,2]

    frame_rgb = frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    try:

        kp2, good_matches = find_good_matches(des1, gray)
        
        if len(good_matches) > MINIMO_SEMELHANCAS:
            BRISK = cv2.drawMatches(original_rgb,kp1,frame_rgb,kp2, good_matches, None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
            cv2.imshow('BRISK features', BRISK)
        else:
            cv2.imshow("BRISK features", frame)
    except:
        pass
    
    
    #Calculando o ângulo da reta que liga o centro dos círculos relação a horizontal.

    font = cv2.FONT_HERSHEY_SIMPLEX

    #Calcula a diferença entre os x0 dos centros dos círculos magenta e azul.
    dx_raiz = circulo1[0] - circulo2[0]
    
    #Transforma em módulo
    dx = abs(dx_raiz)
    
    #Calcula a diferença entre os y0 dos centros dos círculos magenta e azul.
    dy_raiz = circulo1[1] - circulo2[1]

    #Transforma em módulo
    dy = abs(dy_raiz)
    
    #Calcula a distância entre os pontos x0 e y0 dos círculos magenta e azul.
    d = math.sqrt(dx * dx + dy * dy)
    
    #Correção para que não ocorra divisao por zero.
    if d == 0:
        d = 1

    #Calcula a distância da folha até a webcam, pela relação utilizando a distância focal, 
    D = 14*550 / d

    #Condição para failsafe.
    if dy_raiz != 0 and dx_raiz != 0:

        #Calcula o coeficiente angular da reta.
        a = dy_raiz / dx_raiz

        #Calcula o ângulo em relação a horizontal em radianos.
        ang = math.atan(a)

        #Converte o ângulo para graus.
        ang_degree = ang * 180 / math.pi
    
    #Condição para failsafe.
    else:
        a = 0
        ang = 0
        ang_degree = 0
    
    #Printa na tela os valores da distância da folha até a webcam e o ângulo em relação a horizontal 
    #cv2.putText(bgr,'Distance:{} cm'.format(D),(0,100), font, 1,(255,255,255),2,cv2.LINE_AA)
    #cv2.putText(bgr,'Angle:{} graus'.format(ang_degree),(0,150), font, 1,(255,255,255),2,cv2.LINE_AA)
    #cv2.putText(bgr,'Para pedir pra sair aperte "q:',(0,50), font, 1,(255,255,255),2,cv2.LINE_AA)

    #Plota o círculos com o inRange e os contornos destes em duas janelas.
    #cv2.imshow('circulos', bgr)
    #cv2.imshow('preechimento',image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()