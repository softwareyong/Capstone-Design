################################
########## 1번 자동차 ###########
####      출발지 (1,1)      ####
################################

# import os # # os.system(command)
# import json
# import threading
# ds == delivery service

#-*-coding:utf-8-*-
import cv2
from pyzbar import pyzbar # 바코드 인식
import RPi.GPIO as GPIO
from AlphaBot2 import AlphaBot2
from TRSensors import TRSensor
import time
import paho.mqtt.client as mqtt # paho-MQTT 패키지 불러오기
from PCA9685 import PCA9685
import subprocess
import netifaces
#from PIL import barcode

def button_callback(channel):
    # global cam
    global area
    global FINAL_DEST
    global flag 
    
    print("Button pressed")
    print("cam on")
    
    #cam = cv2.VideoCapture(-1) 
    #cam = cv2.VideoCapture(0, cv2.CAP_V4L)
    # cam = cv2.VideoCapture(0, cv2.CAP_V4L)
    cam = cv2.VideoCapture("/dev/video0")
    print(flag)
    if flag == False:
        print("버튼 바로 눌림")
        cam.release()
        cv2.destroyAllWindows()

    while flag:
        ret, frame = cam.read()
        #cv2.imwrite("capture.jpg", frame)
        #image = cv2.imread("capture.jpg")
        barcodes = pyzbar.decode(frame)

        for barcode in barcodes:
            #(x,y,w,h) = barcode.rect
           # cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
            barcodeData = barcode.data.decode("utf-8")
            
            print(barcodeData)
            if barcodeData in area.keys():
               FINAL_DEST = area.get(barcodeData)
               beep_on()
               time.sleep(1)
               beep_off()
               flag = False
        
        if flag == False:
            print("카메라 메모리 반납")
            cam.release()
            cv2.destroyAllWindows()
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
def line_tracking(Ab):
    global TR
    global MAXIMUN
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
def start_mqtt_client_interrupt(): # 메시지 인터럽트오면 끝남
    global time_interrupt
    # 좌표받은 후 좌표는 전역변수 real_message="1024"에 저장
    mqttc = mqtt.Client()
    mqttc.connect('localhost', 1883, 60)
    mqttc.subscribe("dsTopic")
    mqttc.on_message = on_message
    mqttc.loop_start()
    
    start_time = time.time()
    while True:
        if time.time()-start_time >= time_interrupt:
            break
        
        time.sleep(1)
    time_interrupt = 60

    mqttc.loop_stop() 
def on_message(mqttc, userdata, message): # MQTT 클라이언트 객체에 콜백 함수 정의
    global receive_packet 
    global STATUS, RUNNING, READY
    global time_interrupt
    global MY_CAR_NUM 
    
    receive_packet = str(message.payload.decode())  # "2024"
    print("receive_packet: ", receive_packet)
    
    # 너 거기가 목적지니까 다음 status로 바꾸라는뜻 ==> ready로
    if receive_packet[-1] == "r":
        print("메시지 수신완료: " + str(message.payload.decode()))
        ("ready상태로 변경")
        STATUS = READY # ready로
        time_interrupt = 1
        
    elif receive_packet[0] == str(MY_CAR_NUM) and receive_packet[1] == '0': # 메시지가 서버가 나에게 보낸거라면(이때만 저장해야함)
        if STATUS == READY: # ready상태인데 신호받으면 무조건 running 상태로 변경
            print("메시지 수신완료: " + str(message.payload.decode()))
            print("status: ready -> running")
            STATUS = RUNNING # 상태바꾸기
            time_interrupt = 1
            
        else: # 충돌알고리즘에서 패킷받기
            print("메시지 수신완료: " + str(message.payload.decode()))   
            time_interrupt = 1
def is_ready_dest(Ab):
    global receive_packet
    global current_location
    global pre_status, pre_direction
    
    if receive_packet[-1] == "r":
        #spin_after_process(Ab) # 후보정
        Ab.r_spin() # 우회전 
        current_location = receive_packet[3] # 시작 y위치 상태 업데이트
        
        # 4. coordinate update & pre_direction update
        pre_status['x'] = int(receive_packet[2])
        pre_status['y'] = int(receive_packet[3])
        pre_direction = 1 # 직진방향   
def mapping_spin(pre_direction, next_direction): # 상하좌우 = 1234
    result = 0
    angle = str(pre_direction)+str(next_direction)
    
    if angle=="11" or angle=="22" or angle=="33" or angle=="44": # 전진
        result = 1
    elif angle=="12" or angle=="21" or angle=="34" or angle=="43": # 180도
        result = 2
    elif angle=="13" or angle=="24" or angle=="32" or angle=="41": # left
        result = 3
    else: # right
        result = 4
    
    return result 
def qr_detect(cam):
    # global cam
    
    ret, frame = cam.read()
    barcodes = pyzbar.decode(frame)
    barcodeData = 1
     
    for barcode in barcodes:
        (x,y,w,h) = barcode.rect
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
        barcodeData = barcode.data.decode("utf-8")

    
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
    # cv2.imshow('image',frame)
    return barcodeData
def qr_detect_after_process(Ab):
    global cam
    
    cam.release() # 카메라 메모리 정리 
    cv2.destroyAllWindows() # 모든 cv2 화면 제거 
    time.sleep(2) # 3초 휴식 ==> cpu쉬게 하기 
    cam = cv2.VideoCapture(-1) # 비디오 다시켜기 
    Ab.setPWMA(16) # 왼쪽  바퀴 전력주기 
    Ab.setPWMB(16) # 오른쪽 바퀴 전력주기 
    Ab.forward() # 전진 
    time.sleep(0.6) # 0.7초간          
    Ab.stop()
def device_to_server_matrix(barcodeData):  # 서버로 좌표 보내기 
    global ADDRESS
    command = "mosquitto_pub -h 192.168.137.211 -t dsTopic -m {}".format("0"+ str(MY_CAR_NUM)+barcodeData[1]+barcodeData[3])
    result = subprocess.run(command, shell=True, capture_output=True)
def next_hop_mapping(Ab):
    global pre_status
    global receive_packet
    global next_direction
    global pre_direction
    global stop_flag # stop flag == 1 되면 멈추라는 뜻 #방향 그전이랑 그대로

    print(pre_status.get('x') ,pre_status.get('y'))
    x = int(receive_packet[2]) - pre_status.get('x') 
    y = int(receive_packet[3]) - pre_status.get('y')
    
    if x==1 and y==0: # forward
        next_direction = 1 

    elif x==-1 and y==0: # back
        next_direction = 2

    elif x==0 and y==1: #left
        next_direction = 3
    
    elif x==0 and y==-1: # right
        next_direction = 4
    
    else: # stop x==0, y==0
        next_direction = pre_direction # 방향같음
        stop_flag = 1
        
    print(pre_direction, next_direction)
    next_angle = mapping_spin(pre_direction, next_direction)
    
    # 3. mapping_spin
    if stop_flag == 1: # stop
        print("좌표매핑에따라 멈춤!!")
        Ab.stop()
        
    elif next_angle == 1: # 전진
        print("좌표매핑에따라 전진!!")
        
    elif next_angle == 2: # 후진
        print("좌표매핑에따라 후진!!")
        Ab.back_spin()
        
    elif next_angle == 3: # 좌회전
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
    Ab.setPWMA(16)
    Ab.setPWMB(16)
    time.sleep(0.2)
    Ab.stop()
def final_definition_detect():
    global MY_CAR_NUM, FINAL_DEST, current_location
    
    command = "mosquitto_pub -h 192.168.137.211 -t dsTopic -m {}".format("0"+ str(MY_CAR_NUM) + str(FINAL_DEST)+ str(current_location) + "d") # o243d ==> 최종목적지를 0번에게 2번로봇이 보낸다. 최종목적지는 3(4,3)번, 현재위치는 2(1,2)번 입니다.
    result = subprocess.run(command, shell=True, capture_output=True)

MY_CAR_NUM = 1
BUZ = 4
Button = 7
current_location = 1 # wait에서 ready로 왔을때마다 업데이트 해주어야 함, 그때만 
FINAL_DEST = 1
flag = True # True되면 최종목적지 tag한거임
time_interrupt = 30
runnung_flag = True

# GPIO init 
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZ, GPIO.OUT)
GPIO.setup(Button,GPIO.IN, GPIO.PUD_UP)
GPIO.setwarnings(False)

# 초기화
beeped = False  # 부저 울림 여부
area = {"Gyeonggido":1, "Chungcheongdo":2, "Jeollado":3, "Gyeongsangdo":4, "Gangwondo":5}
MAXIMUN = 14
ADDRESS = ifconfig() # ipv4
integral = 0
last_proportional = 0
receive_packet = 0 
pre_status = {'x':1, 'y':MY_CAR_NUM} # 출발지
next_direction = pre_direction = 1 # 처음은 앞을 보고 있으니까 초기방향 == 1
GPIO.add_event_detect(Button, GPIO.FALLING, callback=button_callback, bouncetime=300)

# init
obstacle_off() # 장애물센서 off
TR = TRSensor()
Ab = AlphaBot2()
Ab.stop()
start_move(Ab)

# status 정의
STATUS = 1 # 처음은 READY
READY = 1
RUNNING = 2
WAITING = 3
stop_flag = 0

try:
    while True:
        if STATUS == READY: 
            while True:
                pass
                if flag == False:
                    final_definition_detect() # 만약 tag인식하면 서버 좌표 보내기 
                    break
            start_mqtt_client_interrupt() 
            flag = True
            print("목적지찍기 성공")
            print("최종목적지: ", FINAL_DEST)
            beep_off()
            # STATUS = RUNNING
                 
        elif STATUS == RUNNING: 
            print("running상태로 전환합니다.")
            
            # start_mqtt_client_interrupt()  #####테스트용
            next_hop_mapping(Ab)
            spin_after_process(Ab) # 후보정 앞으로 조금 가기
            if stop_flag == 0:
                pass
            else: # 1이면 멈췄다는 뜻
                stop_flag = 0 # stop 초기화
                device_to_server_matrix("(" + str(pre_status['x']) +","+ str(pre_status['y']) + ")")
                start_mqtt_client_interrupt() # 5.mqtt 메시지 receive mode
                next_hop_mapping(Ab) # 6.next dest mapping ==> 어차피 다시 멈출 일 없음
        
            cam = cv2.VideoCapture(0, cv2.CAP_V4L)
            time.sleep(1)
            
            while True:
                Ab.forward()
                line_tracking(Ab) # 1.라인 트레킹
                
                ret, frame = cam.read()
                barcodes = pyzbar.decode(frame)
                barcodeData = 1
                
                for barcode in barcodes:
                    barcodeData = barcode.data.decode("utf-8")
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                # barcodeData = qr_detect() # 2.카메라
                if barcodeData == 1:
                    pass
                else:
                    Ab.stop() # 자동차 멈추기 
                    print("barcode: ", barcodeData, "pre_status: ", pre_status) # (2,2)
                    print("barcode detect !!!")
                    device_to_server_matrix(barcodeData) # 3.서버로 좌표 보내기 
                    qr_detect_after_process(Ab) # 4.qr탐지 후 후보정    
                    start_mqtt_client_interrupt() # 5.mqtt 메시지 receive mode    
                    if receive_packet[-1] == "r":
                        is_ready_dest(Ab) # ready도착
                        print("이제 부터 준비상태입니다. 버튼을 눌러주세요.")
                        cam.release() # 카메라 메모리 정리 
                        cv2.destroyAllWindows() # 모든 cv2 화면 제거 
                        break
                    else: 
                        next_hop_mapping(Ab) # 6.next dest mapping
                        if stop_flag == 0:
                            pass
                        else: # 1이면 멈췄다는 뜻
                            stop_flag = 0 # stop 초기화
                            device_to_server_matrix("(" + str(pre_status['x']) +","+ str(pre_status['y']) + ")")
                            start_mqtt_client_interrupt() # 5.mqtt 메시지 receive mode
                            next_hop_mapping(Ab) # 6.next dest mapping ==> 어차피 다시 멈출 일 없음
                        # stop이라면 여기서 신호를 다시 보내버리고 기달려 여기서 무한대기
                
                        spin_after_process(Ab)
                        if barcodeData[1]+barcodeData[3] == "4"+str(FINAL_DEST): # 목적지 도착했으면 짐 toss
                            print("짐 toss")
                            pwm = PCA9685(0x40, debug=True)
                            pwm.setPWMFreq(50)
                            pwm.setServoPulse(0, 600)
                            time.sleep(2) 
                            pwm.setServoPulse(0, 1200) 
                            time.sleep(2) 
                            pwm.setServoPulse(0, 600)
                        else:    
                            pass
                    #print('---------------------------------------------')
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break  
except KeyboardInterrupt:
    pass 
      
finally:       
# 종료
    cam.release()
    cv2.destroyAllWindows()
    Ab.stop()