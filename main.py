################################
########## 1번 자동차 ###########
####      출발지 (1,1)      ####
################################

# import os # # os.system(command)
# import json
# import threading

#-*-coding:utf-8-*-
import cv2
from pyzbar import pyzbar # 바코드 인식
import RPi.GPIO as GPIO
from AlphaBot2 import AlphaBot2
from TRSensors import TRSensor
import time
import paho.mqtt.client as mqtt # paho-MQTT 패키지 불러오기
import subprocess
import netifaces


BUZ = 4
Button = 7
FINAL_DEST = 1

# while (GPIO.input(Button) != 0):
   
# GPIO init 
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZ, GPIO.OUT)
GPIO.setup(Button,GPIO.IN, GPIO.PUD_UP)

beeped = False  # 부저 울림 여부
area = {"경기도":1, "강원도":2, "경상도":3, "전라도":4, "충청도":5}

def button_callback(area):
    global FINAL_DEST
    print("Button pressed")

    start_time = time.time()  # 현재 시간을 초 단위로 얻음
    print("cam on")
    cam = cv2.VideoCapture(-1) 
    while True:
        ret, frame = cam.read()
        barcodes = pyzbar.decode(frame)
        for barcode in barcodes:
            (x,y,w,h) = barcode.rect
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
            barcodeData = barcode.data.decode("utf-8")
            
            print(barcodeData)
            if barcodeData in area.keys():
               FINAL_DEST = area.get(barcodeData)
               beep_on()
            
        elapsed_time = time.time() - start_time  # 현재 시간에서 시작 시간을 뺌
        if elapsed_time >= 5:
            beep_off()
            break    
            
        # cv2.imshow('image',frame)
        k = cv2.waitKey(10) & 0xFF
        if k == 27:
                break
def beep_on():
    GPIO.output(BUZ, GPIO.HIGH)
def beep_off():
    GPIO.output(BUZ, GPIO.LOW)
def ifconfig():     
    address = 0
    
    interfaces = netifaces.interfaces() # 사용 가능한 인터페이스 정보 가져오기
    for iface in interfaces: # 모바일 핫스팟에 연결된 인터페이스 찾기
        if "wlan" in iface:
            addrs = netifaces.ifaddresses(iface)
            address = addrs[netifaces.AF_INET][0]['addr'] # IPv4  
            break
        
    return address
def obstacle_off():
    # GPIO 핀 번호 설정
    DR = 16
    DL = 19
    # GPIO 핀을 출력 모드로 설정
    GPIO.setup(DR, GPIO.OUT)
    GPIO.setup(DL, GPIO.OUT)
    GPIO.output(DR, GPIO.HIGH)
    GPIO.output(DL, GPIO.HIGH)
def start_move(Ab):
    print("Line follow Example")
    time.sleep(0.5)
    for i in range(0,50):
        if i<12 or i>= 37:
            Ab.init_right()
            Ab.setPWMA(10)
            Ab.setPWMB(10)
        else:
            Ab.init_left()
            Ab.setPWMA(10)
            Ab.setPWMB(10)
        TR.calibrate()
    Ab.stop()
    print(TR.calibratedMin)
    print(TR.calibratedMax)
def line_tracking(Ab, TR):
    global last_proportional 
    global integral
    
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

        if (power_difference > MAXIMUN):
            power_difference = MAXIMUN
        if (power_difference < - MAXIMUN):
            power_difference = - MAXIMUN
        if (power_difference < 0):
            Ab.setPWMA(MAXIMUN + power_difference)
            Ab.setPWMB(MAXIMUN)
        else:
            Ab.setPWMA(MAXIMUN)
            Ab.setPWMB(MAXIMUN - power_difference)
def start_mqtt_client():
    # 좌표받은 후 좌표는 전역변수 real_message="1024"에 저장
    mqttc = mqtt.Client()
    mqttc.connect('localhost', 1883, 60)
    mqttc.subscribe("dsTopic")
    mqttc.on_message = on_message
    # mqttc.loop_forever()
    mqttc.loop_start()
    time.sleep(8)##############################################
    mqttc.loop_stop()
def on_message(mqttc, userdata, message): # MQTT 클라이언트 객체에 콜백 함수 정의
    # global message_count
    # message_count += 1
    # print(f"수신된 메시지 수: {message_count}")
    global receive_packet 
    receive_packet = str(message.payload.decode())  # "1024"
    
    if receive_packet[0] == '1' and  receive_packet[1] == '0': # 메시지가 서버가 나에게 보낸거라면(이때만 저장해야함)
        print("메시지 수신완료: " + str(message.payload.decode()))
def mapping_spin(pre_direction, next_direction): # 전진:1, 좌회전:2, 우회전:3
    result = 0
    if pre_direction == 1: # 전에 전진
        if next_direction == 1: # 전전
            result = 1
        elif next_direction == 2: # 전왼
            result = 2
        else: # 전오
            result = 3
                
    elif pre_direction == 2: # 전에 왼쪽
        if next_direction == 1: # 왼전
            result = 3
        else: # 왼왼
            result = 1
        
    else: # 전에 오른쪽
        if next_direction == 1: # 오전
            result = 2
        else: # 오오
            result = 1

    return result
def qr_detect():
    global cam
    
    ret, frame = cam.read()
    barcodes = pyzbar.decode(frame)
    barcodeData = 1
     
    for barcode in barcodes:
        (x,y,w,h) = barcode.rect
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
        barcodeData = barcode.data.decode("utf-8")

    # cv2.imshow('image',frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
    return barcodeData
def qr_detect_after_process(Ab):
    global cam
    
    cam.release() # 카메라 메모리 정리 
    cv2.destroyAllWindows() # 모든 cv2 화면 제거 
    Ab.stop() # 자동차 멈추기 
    time.sleep(3) # 3초 휴식 ==> cpu쉬게 하기 
    
    cam = cv2.VideoCapture(-1) # 비디오 다시켜기 
    Ab.setPWMA(14) # 왼쪽  바퀴 전력주기 
    Ab.setPWMB(14) # 오른쪽 바퀴 전력주기 
    Ab.forward() # 전진 
    time.sleep(0.6) # 0.6초간 
    Ab.stop()
def device_to_server_matrix(barcodeData):  # 서버로 좌표 보내기 
    command = "mosquitto_pub -h 192.168.137.4 -t dsTopic -m {}".format("01"+barcodeData[1]+barcodeData[3])
    result = subprocess.run(command, shell=True, capture_output=True)
    
    global cam
    
    cam.release() # 카메라 메모리 정리 
    cv2.destroyAllWindows() # 모든 cv2 화면 제거 
    Ab.stop() # 자동차 멈추기 
    time.sleep(3) # 3초 휴식 ==> cpu쉬게 하기 
    
    cam = cv2.VideoCapture(-1) # 비디오 다시켜기 
    Ab.setPWMA(14) # 왼쪽  바퀴 전력주기 
    Ab.setPWMB(14) # 오른쪽 바퀴 전력주기 
    Ab.forward() # 전진 
    time.sleep(0.6) # 0.6초간 
    Ab.stop()
def next_hop_mapping(Ab):
    global pre_status
    global receive_packet
    global next_direction
    global pre_direction
    
    print(pre_status.get('x') ,pre_status.get('y'))
    x = int(receive_packet[2]) - pre_status.get('x') 
    y = int(receive_packet[3]) - pre_status.get('y')
    if x==0 and y==1: # forward
        next_direction = 1 
        
    elif x==-1 and y==0: # left
        next_direction = 2
        
    else: # right
        next_direction = 3
        
    print(pre_direction, next_direction)
    # 3. mapping_spin
    if mapping_spin(pre_direction, next_direction)==1: # 전진
        print("좌표매핑에따라 전진!!")
        Ab.lt_forward()
        
    elif mapping_spin(pre_direction, next_direction)==2:  # 좌회전
        print("좌표매핑에따라 좌회전!!")
        Ab.l_spin()
        
    else: # 우회전
        print("좌표매핑에따라 우회전!!")
        Ab.r_spin()

    # 4. coordinate update & pre_direction update
    pre_status['x'] = int(receive_packet[2])
    pre_status['y'] = int(receive_packet[3])
    pre_direction = next_direction
def spin_after_process(Ab):
    Ab.forward()
    Ab.setPWMA(15)
    Ab.setPWMB(15)
    time.sleep(0.1)

# 초기화
MAXIMUN = 12
ADDRESS = ifconfig()
integral = 0
last_proportional = 0
receive_packet = 0 
pre_status = {'x':1, 'y':1} # 출발지
next_direction = pre_direction = 1 # 처음은 앞을 보고 있으니까 초기방향 == 1

# init
obstacle_off() # 장애물센서 off
TR = TRSensor()
Ab = AlphaBot2()
Ab.stop()
start_move(Ab)
cam = cv2.VideoCapture(-1) 
time.sleep(2)
Ab.forward()

while(True):
    
    line_tracking(Ab, TR) # 1.라인 트레킹
    barcodeData = qr_detect() # 2.카메라
     
    if barcodeData == 1:
        pass
    else:
        print(barcodeData)
        print("barcode: ", barcodeData, "pre_status: ", pre_status) # (2, 2)
        print("barcode detect !!!")
        device_to_server_matrix(barcodeData) # 3.서버로 좌표 보내기 
        qr_detect_after_process(Ab) # 4.qr탐지 후 후보정        
        start_mqtt_client() # 5.mqtt 메시지 receive mode 
        next_hop_mapping(Ab) # 6.next dest mapping
        spin_after_process(Ab) # 7.스핀 후 후보정
    
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break  
            
# 종료
cam.release()
cv2.destroyAllWindows()
Ab.stop()
