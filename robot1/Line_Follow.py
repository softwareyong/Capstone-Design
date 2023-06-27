#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
from AlphaBot2 import AlphaBot2
from TRSensors import TRSensor
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


maximum = 15
integral = 0
last_proportional = 0

TR = TRSensor()
Ab = AlphaBot2()
Ab.stop()
print("Line follow Example")
time.sleep(0.5)
for i in range(0,50):
   if(i<12 or i>= 37):
      Ab.right()
      Ab.setPWMA(10)
      Ab.setPWMB(10)
   else:
      Ab.left()
      Ab.setPWMA(10)
      Ab.setPWMB(10)
   TR.calibrate()
Ab.stop()
print(TR.calibratedMin)
print(TR.calibratedMax)
Ab.forward()

while True:
   try:
      position,Sensors = TR.readLine()
      #print(position)
      if(Sensors[0] >900 and Sensors[1] >900 and Sensors[2] >900 and Sensors[3] >900 and Sensors[4] >900):
         Ab.setPWMA(0)
         Ab.setPWMB(0)
      else:
         # The "proportional" term should be 0 when we are on the line.
         proportional = position - 2000
         
         # Compute the derivative (change) and integral (sum) of the position.
         derivative = proportional - last_proportional
         integral += proportional
         
         # Remember the last position.
         last_proportional = proportional

         power_difference = proportional/30  + integral/10000 + derivative*2;  

         if (power_difference > maximum):
            power_difference = maximum
         if (power_difference < - maximum):
            power_difference = - maximum
         if (power_difference < 0):
            Ab.setPWMA(maximum + power_difference)
            Ab.setPWMB(maximum)
         else:
            Ab.setPWMA(maximum)
            Ab.setPWMB(maximum - power_difference)
         
   except KeyboardInterrupt:
      break