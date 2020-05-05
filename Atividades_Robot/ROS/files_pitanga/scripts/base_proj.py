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

w = 0.1
v = 0.2

frame = "camera_link"
# frame = "head_camera"  # DESCOMENTE para usar com webcam USB via roslaunch tag_tracking usbcam

tfl = 0

tf_buffer = tf2_ros.Buffer()

bridge = CvBridge()

cv_image = None
media = []
centro = []
atraso = 1.5E9 # 1 segundo e meio. Em nanossegundos

area = 0.0 # Variavel com a area do maior contorno

# Só usar se os relógios ROS da Raspberry e do Linux desktop estiverem sincronizados. 
# Descarta imagens que chegam atrasadas demais
check_delay = False 

# A função a seguir é chamada sempre que chega um novo frame
def roda_todo_frame(imagem):
    print("frame")
    global cv_image
    global media
    global centro
    global resultados

    now = rospy.get_rostime()
    imgtime = imagem.header.stamp
    lag = now-imgtime # calcula o lag
    delay = lag.nsecs
    # print("delay ", "{:.3f}".format(delay/1.0E9))
    if delay > atraso and check_delay==True:
        print("Descartando por causa do delay do frame:", delay)
        return 
    try:
        antes = time.clock()
        temp_image = bridge.compressed_imgmsg_to_cv2(imagem, "bgr8")
        # Note que os resultados já são guardados automaticamente na variável
        # chamada resultados
        centro, saida_net, resultados =  visao_module.processa(temp_image)        
        for r in resultados:
            # print(r) - print feito para documentar e entender
            # o resultado            
            pass

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

		print(tf_buffer.can_transform(frame, marcador, rospy.Time(0)))
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
		print("id: {} x {} y {} z {} angulo {} ".format(id, x,y,z, angulo_marcador_robo))

#====================== tratamento de eventos ============================

faixa_creeper = 5

faixa_ponto_fuga = 3

d = 0.4


coef_angular_positivo = []
coef_angular_negativo = []
coef_linear_positivo = []
coef_linear_negativo = []

mediana_x = 0
mediana_y = 0

if __name__=="__main__":

	print("Coordenadas configuradas para usar robô virtual, para usar webcam USB altere no código fonte a variável frame")

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
				ponto_fuga = atividade3_projeto.ponto_fuga(cv_image)

				if len(centro) and len(media)!= 0:
					#print(leitura_scan)

					#Codigo para identificar o creeper pela cor

					if leitura_scan <= d and leitura_scan != 0:
						vel = Twist(Vector3(0,0,0), Vector3(0,0,0))
					
					if leitura_scan > d:
						if media[0] + faixa_creeper < centro[0]:
							vel = Twist(Vector3(0,0,0), Vector3(0,0,w))

						elif media[0] - faixa_creeper > centro[0]:
							vel = Twist(Vector3(0,0,0), Vector3(0,0,-w))

						if abs(media[0] - centro[0]) <= faixa_creeper:
							vel = Twist(Vector3(v,0,0), Vector3(0,0,0))

						#Codigo com o robo na pista
						
						#if ponto_fuga[0] + faixa_ponto_fuga < centro[0]:
						#	vel = Twist(Vector3(0,0,0), Vector3(0,0,w))

						#elif ponto_fuga[0] - faixa_ponto_fuga > centro[0]:
						#	vel = Twist(Vector3(0,0,0), Vector3(0,0,-w))
						
						#if abs(ponto_fuga[0] - centro[0]) <= faixa_ponto_fuga:
						#	vel = Twist(Vector3(v,0,0), Vector3(0,0,0))
				else:
					vel = Twist(Vector3(0,0,0), Vector3(0,0,0))

				velocidade_saida.publish(vel)

				# Note que o imshow precisa ficar *ou* no codigo de tratamento de eventos *ou* no thread principal, não em ambos
				cv2.imshow("cv_image no loop principal", cv_image)
				cv2.waitKey(1)
				rospy.sleep(0.1)

	except rospy.ROSInterruptException:
	    print("Ocorreu uma exceção com o rospy")