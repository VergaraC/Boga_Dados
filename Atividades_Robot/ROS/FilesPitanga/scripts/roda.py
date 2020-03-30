#! /usr/bin/env python
# -*- coding:utf-8 -*-

import rospy
from geometry_msgs.msg import Twist, Vector3
from time import sleep
import math

v = 0.2  # Velocidade linear
w = math.pi/6  # Velocidade angular


def up():
    vel = Twist(Vector3(v,0,0), Vector3(0,0,0))
    pub.publish(vel)
    rospy.sleep(5)

def down():
    vel = Twist(Vector3(-v,0,0), Vector3(0,0,0))
    pub.publish(vel)
    rospy.sleep(5)

def right():
    vel = Twist(Vector3(0,0,0), Vector3(0,0,-w))
    pub.publish(vel)
    rospy.sleep(3)
    

def left():
    vel = Twist(Vector3(0,0,0), Vector3(0,0,w))
    pub.publish(vel)
    rospy.sleep(3)


def stop():
    vel = Twist(Vector3(0,0,0), Vector3(0,0,0))
    pub.publish(vel)
    rospy.sleep(0.5)

def quadrado():
    right()
    stop()
    up()
    stop()
    right()
    stop()
    up()
    stop()
    right()
    stop()
    up()
    stop()
    right()
    stop()
    up()
    stop()


if __name__ == "__main__":
    rospy.init_node("roda_exemplo")
    pub = rospy.Publisher("cmd_vel", Twist, queue_size=3)

    try:
        while not rospy.is_shutdown():
            quadrado()            
            
    except rospy.ROSInterruptException:
        print("Ocorreu uma exceção o com o rospy")