#! /usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = ["Rachel P. B. Moraes", "Fabio Miranda"]

import rospy
import numpy as np
from numpy import linalg
from tf import transformations
from tf import TransformerROS
import tf2_ros
import cv2

import math
from geometry_msgs.msg import Twist, Vector3, Pose, Vector3Stamped
from ar_track_alvar_msgs.msg import AlvarMarker, AlvarMarkers
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Image, CompressedImage
from std_msgs.msg import Header
from sensor_msgs.msg import LaserScan
from cv_bridge import CvBridge, CvBridgeError
import cormodule
import time

import atividade3_projeto
import visao_module

x = 0
y = 0
z = 0 
id = 0

leitura_scan = 0

w = 0.08
v = 0.1

frame = "camera_link"
# frame = "head_camera"  # DESCOMENTE para usar com webcam USB via roslaunch tag_tracking usbcam

tfl = 0

tf_buffer = tf2_ros.Buffer()

bridge = CvBridge()

cv_image = None
img_cor = None
media = []
centro = []
atraso = 1.5E9 # 1 segundo e meio. Em nanossegundos

centro_estacao = 0

#CLASSES = [ "bicycle", "bird","cat","dog"]
station_MNet="cat"

area = 0.0 # Variavel com a area do maior contorno

# Só usar se os relógios ROS da Raspberry e do Linux desktop estiverem sincronizados. 
# Descarta imagens que chegam atrasadas demais
check_delay = False 

# A função a seguir é chamada sempre que chega um novo frame
def roda_todo_frame(imagem):
    #print("frame")
    global cv_image
    global media
    global centro
    global resultados
    global img_cor
    global area
    global centro_estacao

    now = rospy.get_rostime()
    imgtime = imagem.header.stamp
    lag = now-imgtime # calcula o lag
    delay = lag.nsecs
    # print("delay ", "{:.3f}".format(delay/1.0E9))
    #if delay > atraso and check_delay==True:
    #    print("Descartando por causa do delay do frame:", delay)
    #    return 
    try:
        antes = time.clock()
        temp_image = bridge.compressed_imgmsg_to_cv2(imagem, "bgr8")
        # Note que os resultados já são guardados automaticamente na variável
        # chamada resultados
        # Parte MobileNet  - rede neural
        centro, saida_net, resultados =  visao_module.processa(temp_image)        
        centro_estacao=0
        for result in resultados:
            if result[0] == station_MNet and result[1] >= 50:
                xi = result[2][0]
                xf = result[3][0]
                centro_estacao = (xi+xf)/2

        # Parte cor:

        media, centro, img_cor, area = visao_module.identifica_cor(temp_image) 
        

        depois = time.clock()
        # Desnecessário - Hough e MobileNet já abrem janelas
        cv_image = saida_net.copy()
    except CvBridgeError as e:
        print('ex', e)
#========================= le_scan =========================

def scaneou(dado):
    global leitura_scan
    leitura_scan = np.array(dado.ranges[0]).round(decimals=2)

def recebe(msg):
    global x # O global impede a recriacao de uma variavel local, para podermos usar o x global ja'  declarado
    global y
    global z
    global id
    for marker in msg.markers:
        id = marker.id
        marcador = "ar_marker_" + str(id)

        #print(tf_buffer.can_transform(frame, marcador, rospy.Time(0)))
        header = Header(frame_id=marcador)
        # Procura a transformacao em sistema de coordenadas entre a base do robo e o marcador numero 100
        # Note que para seu projeto 1 voce nao vai precisar de nada que tem abaixo, a 
        # Nao ser que queira levar angulos em conta
        trans = tf_buffer.lookup_transform(frame, marcador, rospy.Time(0))
        
        # Separa as translacoes das rotacoes
        x = trans.transform.translation.x
        y = trans.transform.translation.y
        z = trans.transform.translation.z
        # ATENCAO: tudo o que vem a seguir e'  so para calcular um angulo
        # Para medirmos o angulo entre marcador e robo vamos projetar o eixo Z do marcador (perpendicular) 
        # no eixo X do robo (que e'  a direcao para a frente)
        t = transformations.translation_matrix([x, y, z])
        # Encontra as rotacoes e cria uma matriz de rotacao a partir dos quaternions
        r = transformations.quaternion_matrix([trans.transform.rotation.x, trans.transform.rotation.y, trans.transform.rotation.z, trans.transform.rotation.w])
        m = np.dot(r,t) # Criamos a matriz composta por translacoes e rotacoes
        z_marker = [0,0,1,0] # Sao 4 coordenadas porque e'  um vetor em coordenadas homogeneas
        v2 = np.dot(m, z_marker)
        v2_n = v2[0:-1] # Descartamos a ultima posicao
        n2 = v2_n/linalg.norm(v2_n) # Normalizamos o vetor
        x_robo = [1,0,0]
        cosa = np.dot(n2, x_robo) # Projecao do vetor normal ao marcador no x do robo
        angulo_marcador_robo = math.degrees(math.acos(cosa))
        
        # Terminamos
        #print("id: {} x {} y {} z {} angulo {} ".format(id, x,y,z, angulo_marcador_robo))

#====================== tratamento de eventos ============================

faixa_creeper = 20

faixa_ponto_fuga = 20

faixa_estacao = 20

d = 0.3

status_creeper=False

coef_angular_positivo = []
coef_angular_negativo = []
coef_linear_positivo = []
coef_linear_negativo = []

mediana_x = 0
mediana_y = 0

id_creeper = 0


#funções de ações do robô =======================================



def anda_pista(centro_robo, ponto_fuga, faixa_ponto_fuga,v,w):
    if ponto_fuga + faixa_ponto_fuga < centro_robo:
        print('direita')
        vel = Twist(Vector3(0,0,0), Vector3(0,0,w))

    elif ponto_fuga - faixa_ponto_fuga > centro_robo:
        print('esquerda')
        vel = Twist(Vector3(0,0,0), Vector3(0,0,-w))
    
    if abs(ponto_fuga - centro_robo) <= faixa_ponto_fuga:
        print('reto')
        vel = Twist(Vector3(v,0,0), Vector3(0,0,0))
    
    return vel

def procurando_creeper(centro_creeper, centro_robo, faixa_creeper, v, w):
    if centro_creeper + faixa_creeper < centro_robo:
        print('procurando creeper')
        vel = Twist(Vector3(0,0,0), Vector3(0,0,w))

    elif centro_creeper - faixa_creeper > centro_robo:
        print('procurando creeper')
        vel = Twist(Vector3(0,0,0), Vector3(0,0,-w))

    if abs(centro_creeper - centro_robo) <= faixa_creeper:
        print('achei o creeper')
        vel = Twist(Vector3(v,0,0), Vector3(0,0,0))
    
    return vel

def parar():
    vel = Twist(Vector3(0,0,0), Vector3(0,0,0))
    return vel

def procurar_pista(v,w):
    w = 0.1
    vel = Twist(Vector3(0,0,0), Vector3(0,0,-w))
    return vel

def dar_re(v):
    v = -0.1
    vel = Twist(Vector3(v,0,0), Vector3(0,0,0))
    return vel

def procura_estacao(centro_estacao, centro_robo, faixa_estacao, leitura_scan, v, w):

    if centro_estacao + faixa_estacao < centro_robo and leitura_scan > 0.3:
        vel = Twist(Vector3(0,0,0), Vector3(0,0,w))
        print('procurando estação')
    
    elif centro_estacao - faixa_estacao > centro_robo and leitura_scan > 0.3:
        vel = Twist(Vector3(0,0,0), Vector3(0,0,-w))
        print('procurando estação')

    if abs(centro_estacao - centro_robo) <= faixa_estacao and leitura_scan > 0.3:
        vel = Twist(Vector3(v,0,0), Vector3(0,0,0))
        print('achei a estação')
    
    if leitura_scan <= 0.3:
        parar()
        print('parei')
        print('')
        print('SOLTE O CREEPER')
        raw_input()
    
    return vel

#main ==================================================================


if __name__=="__main__":

    #print("Coordenadas configuradas para usar robô virtual, para usar webcam USB altere no código fonte a variável frame")

    rospy.init_node("marcador") # Como nosso programa declara  seu nome para o sistema ROS

    topico_imagem = "/camera/rgb/image_raw/compressed"

    recebedor2 = rospy.Subscriber(topico_imagem, CompressedImage, roda_todo_frame, queue_size=4, buff_size = 2**24)
    recebedor = rospy.Subscriber("/ar_pose_marker", AlvarMarkers, recebe) # Para recebermos notificacoes de que marcadores foram vistos
    velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 1) # Para podermos controlar o robo
    recebe_scan = rospy.Subscriber("/scan", LaserScan, scaneou)

    tfl = tf2_ros.TransformListener(tf_buffer) # Para fazer conversao de sistemas de coordenadas - usado para calcular angulo

    # Exemplo de categoria de resultados
    # [('chair', 86.965459585189819, (90, 141), (177, 265))]

    # Inicializando - por default gira no sentido anti-horário
    # vel = Twist(Vector3(0,0,0), Vector3(0,0,math.pi/10.0))

#================================
#Para atividade 5
    #Verde -> id=3
    #Azul -> id=2
    #Roxo -> id=1
#================================
    vel = Twist(Vector3(0,0,0), Vector3(0,0,0))
    try:
        while not rospy.is_shutdown():
            if cv_image is not None:
                try:
                    ponto_fuga = atividade3_projeto.ponto_fuga(cv_image)
                    print('ponto fuga')
                    print(ponto_fuga)
                except:
                    pass

                if len(centro) and len(media) != 0:
                    print('leitura scan')
                    print(leitura_scan)
                
                    print("Area:",area)
                    if area >= 3000 and status_creeper == False:
                        vel = procurando_creeper(media[0], centro[0], faixa_creeper, v, w)
                        if leitura_scan <= d:
                            vel = parar()
                            status_creeper = True
                            print('USE A GARRA')
                            raw_input()

                            #posição inicial da garra para pegar o creeper 
                            #x: 0.300
                            #y: 0
                            #z: 0.304
                            #Greeper: 0.02

                            #posição depois de pegar o creeper:
                            #setar home pose

                    elif status_creeper == True and centro_estacao!=0:
                        procura_estacao(centro_estacao, centro[0], faixa_estacao, leitura_scan, v, w)
                        
                    elif status_creeper==True:
                        vel = procurar_pista(v,w)

                    else:
                        vel = anda_pista(centro[0], ponto_fuga[0], faixa_ponto_fuga, v, w)
                    
                    if leitura_scan <= 0.7 and status_creeper==True:
                        vel = dar_re(v)

                    if ponto_fuga[0] != 0 and status_creeper == True:
                        vel = anda_pista(centro[0], ponto_fuga[0], faixa_ponto_fuga, v, w)
                    
                else:
                    print('parado')
                    vel = Twist(Vector3(0,0,0), Vector3(0,0,0))

                velocidade_saida.publish(vel)

                # Note que o imshow precisa ficar *ou* no codigo de tratamento de eventos *ou* no thread principal, não em ambos
                cv2.imshow("cv_image no loop principal", cv_image)
                cv2.waitKey(1)
                if img_cor is not None:
                    cv2.imshow("DEBUG", img_cor) 
                    cv2.waitKey(1)
                else:
                    print("cor_debug is null")

                rospy.sleep(0.05)

    except rospy.ROSInterruptException:
        print("Ocorreu uma exceção com o rospy")