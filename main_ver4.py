################################
########## 1번 자동차 ###########
################################

#-*-coding:utf-8-*-
import cv2
from pyzbar import pyzbar # 바코드 인식
# import argparse # 이미지 처리할 때 쓰는거
# import imutils # 이미지 처리
import RPi.GPIO as GPIO
from AlphaBot2 import AlphaBot2
from TRSensors import TRSensor
import time
import os
import paho.mqtt.client as mqtt # paho-MQTT 패키지 불러오기
import json
import subprocess
import threading

global real_message ##########################################################################################3
global flag 
flag = 0

def start_move(Ab):
    print("Line follow Example")
    time.sleep(0.5)
    for i in range(0,50):
        if i<12 or i>= 37:
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
    # time.sleep(0.1)
    # Ab.forward()


def video_stream(Ab, qr_detect, cam):
    ret, frame = cam.read()
    barcodes = pyzbar.decode(frame) # 바코드 여러개 있을 때 대비
    barcodeData = False # 초기화 [1,2,3]
    
    for barcode in barcodes:
        (x,y,w,h) = barcode.rect
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2) # bounding box
        barcodeData = barcode.data.decode("utf-8") # (2,1)정보 담김
    
    cv2.imshow('image',frame)
    return frame


def rine_tracking(Ab, TR):
    position,Sensors = TR.readLine()
    if(Sensors[0] >900 and Sensors[1] >900 and Sensors[2] >900 and Sensors[3] >900 and Sensors[4] >900):
        Ab.setPWMA(0)
        Ab.setPWMB(0)
    else:
        proportional = position - 2000
        derivative = proportional - last_proportional
        integral += proportional
         
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

def start_mqtt_client():
    mqttc = mqtt.Client()
    mqttc.connect('localhost', 1883, 60)
    mqttc.subscribe("dsTopic")
    mqttc.on_message = on_message
    # print(mqttc.on_message.payload.decode())
    # print("a:", a)
    # x = mqttc.on_message
    # print(x)
    # print(mqttc.on_message)
    # mqttc.loop_forever()
    mqttc.loop_start()
    time.sleep(15)
    mqttc.loop_stop()
    # if flag == 1:
    #     mqttc.loop_stop()
    #     flag = 0
        
    # mqttc.loop_start()

# MQTT 클라이언트 객체에 콜백 함수 정의
def on_message(mqttc, userdata, message):
    # global message_count
    # message_count += 1
    # print(f"수신된 메시지 수: {message_count}")
    # get_cooprdinate(str(message.payload.decode()))
    # message = str(message.payload.decode())
    real_message = str(message.payload.decode())  # "1024"
    
    if real_message[0] == '1':
        print("Received message: " + str(message.payload.decode()))
    
    # if real_message[0] == '1' and  real_message[1] == '0':
        print("탈출완료")
        flag = 1
            # 메시지 수신 후 루프 종료
        mqttc.loop_stop()
            
 
    # return message
    
    # a = message
    # return message

# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)

# # 초기화
maximum = 12 # 고유속도 9가 좋음 ############################a##########################################################33
integral = 0
last_proportional = 0
TR = TRSensor()
Ab = AlphaBot2()
Ab.stop()

# # 시작 
start_move(Ab)
cam = cv2.VideoCapture(-1) 
Ab.forward()

while(True):
    position,Sensors = TR.readLine()
    if(Sensors[0] >900 and Sensors[1] >900 and Sensors[2] >900 and Sensors[3] >900 and Sensors[4] >900):
        Ab.setPWMA(0)
        Ab.setPWMB(0)
    else:
        proportional = position - 2000
        derivative = proportional - last_proportional
        integral += proportional
         
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

    # 카메라
    # time.sleep(10)
    ret, frame = cam.read()
    barcodes = pyzbar.decode(frame)
    barcodeData = 1
     
    for barcode in barcodes:
            (x,y,w,h) = barcode.rect
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
            barcodeData = barcode.data.decode("utf-8")

    # cv2.imshow('image',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # print(barcodeData)
    if barcodeData == 1 :
        pass
    else: 
        print(barcodeData) # (2, 2)
        # data = [0, 1, {"matrix":barcodeData[1:-1]}]
        # message = json.dumps(data)
        # message = {"matrix":barcodeData[1:-1]}
        
        command = "mosquitto_pub -h 192.168.137.4 -t dsTopic -m {}".format("01"+barcodeData[1]+barcodeData[3])
        result = subprocess.run(command, shell=True, capture_output=True)
        # print(result)
        # os.system(command)
        print("barcode detect!!!!!!!!@@@@@")
        cam.release()
        cv2.destroyAllWindows()
        Ab.stop()
        time.sleep(5)
        cam = cv2.VideoCapture(-1)
        Ab.setPWMA(10)
        Ab.setPWMB(10)
        Ab.forward()
        time.sleep(1.5)
        
        # 무한대기 ==> 다시 좌표가 올때까지 무한대기
        print("무한 지옥 시작")
        Ab.stop()
        start_mqtt_client()
        # mqttc = mqtt.Client()
        # mqttc.connect('localhost', 1883, 60)
        # mqttc.subscribe("dsTopic")
        # mqttc.on_message = on_message
        # mqttc.loop_forever()
        # mqttc.loop_stop()
        # mqttc.disconnect()
        
        ############지옥의 악마선################
        print("무한지옥 종료")
        Ab.setPWMA(10)
        Ab.setPWMB(10)
        Ab.forward()
            

cam.release()
cv2.destroyAllWindows()
Ab.stop()
