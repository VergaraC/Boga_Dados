#! /usr/bin/env python
# -*- coding:utf-8 -*-


import rospy
import numpy as np
from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import LaserScan

leitura_scan = 0

def scaneou(dado):
	#print("Faixa valida: ", dado.range_min , " - ", dado.range_max )
	global leitura_scan
	leitura_scan = np.array(dado.ranges[0]).round(decimals=2)
	#wall_distance = leitura_scan
	#print("Intensities")
	#print(np.array(dado.intensities).round(decimals=2))

if __name__=="__main__":

	rospy.init_node("le_scan")

	velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 3 )
	recebe_scan = rospy.Subscriber("/scan", LaserScan, scaneou)
	
	while not rospy.is_shutdown():
		if leitura_scan < 1:
			velocidade = Twist(Vector3(-0.2, 0, 0), Vector3(0, 0, 0))
			velocidade_saida.publish(velocidade)
		elif leitura_scan >= 1.02:
			velocidade = Twist(Vector3(0.2, 0, 0), Vector3(0, 0, 0))
			velocidade_saida.publish(velocidade)