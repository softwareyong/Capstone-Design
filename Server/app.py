from flask import Flask, render_template, request
import threading
import paho.mqtt.client as mqtt # paho-MQTT 패키지 불러오기
import subprocess
import time
app = Flask(__name__)

###################
#   robot status  # 
#   1 ==  READY   #
#   2 == RUNNING  #
#   3 == WAITING  #
###################

@app.route('/', methods=['GET', 'POST'])
def index():
    global info_1, info_2
    global robots
    ##### info 이름을 bot이 가져온 변수로 변경할 것

    # if request.method == 'POST':
    info_1 = {'rec' : 1,'send' : 4, 'mtx_x' : robots[1]['now'][0], 'mtx_y' : robots[1]['now'][1] } # 형식을 json으로 변경
    info_2 = {'rec' : 2,'send' : 4, 'mtx_x' : robots[2]['now'][0], 'mtx_y' : robots[2]['now'][1] } # 형식을 json으로 변경
    return render_template("index.html",info1=info_1,info2=info_2) ##### info를 로봇이 가져온 변수로 변경할 것

@app.route('/update_html')
def update_html():
    # 로봇 좌표를 가져와서 index.html을 렌더링하여 응답으로 전송
    global info_1, info_2, robots
    info_1 = {'rec': 1, 'send': 4, 'mtx_x': robots[1]['now'][0], 'mtx_y': robots[1]['now'][1]}
    info_2 = {'rec': 2, 'send': 4, 'mtx_x': robots[2]['now'][0], 'mtx_y': robots[2]['now'][1]}
    return render_template("index.html", info1=info_1, info2=info_2)

def start_mqtt_client():
    mqttc = mqtt.Client()
    mqttc.connect('localhost', 1883, 60)
    mqttc.subscribe("dsTopic")
    mqttc.on_message = on_message
    mqttc.loop_forever()
    # mqttc.loop_start()
def robot_arrive_chk(): # 모든 로봇들이 왔는지 체크하는 함수 
    global ready_q, running_q, waiting_q
    global robot
def is_dest_ready(robot_num):
    global robots
    global waiting_q, ready_q
    
    print("now, waitdest비교", robots[robot_num]['now'], robots[robot_num]['waitdest'])
    if robots[robot_num]['now'] == robots[robot_num]['waitdest']: #1,0 ==> # ready목적지에 도착했다면 
        
        # 1. [q] 상태 업데이트
        ready_q.append(robots[robot_num]['num']) # ready mode ON
        waiting_q.remove(robots[robot_num]['num']) # waiting mode OFF
    
        # 2. [robot] 상태 업데이트
        robots[robot_num]['status'] = 1 # ready
        robots[robot_num]['waitdest'] = "" # 
        print(robot_num, "번의 로봇이 ready로 변환합니다. 좌표는", robots[robot_num]['now'])      
def is_key_dest(robot_num):
# key dest에 도착했는지 물어보는 함수
    global robots, waiting_q
    cnt = 0

    if robots[robot_num]['now'] == "10": #1,0 ==> # key point에 도착했다면 
        print("로봇이 key point에 도착했습니다.")
        if len(waiting_q) == 2: # 웨이팅이 2명이면
            if waiting_q[0] == robot_num:
                other_robot_num = waiting_q[1]
                
            elif waiting_q[1] == robot_num: 
                other_robot_num = waiting_q[0]
            
            if robots[other_robot_num]['now'][0] == "1": # 다른로봇이 앞에 있다면 
                robots[robot_num]['waitdest'] = "14"
            
            else: # 다른로봇이 내 뒤에 있다면
                robots[robot_num]['waitdest'] = "15" # 내가 첫번째 ready
 
        else: # 웨이팅상태가 혼자라면 
            robots[robot_num]['waitdest'] = "15"

        # ready로 바뀔 때 ==> waitdest를 지워주어서 
        # waiting상태 중 waitdest에 있을때만, wait_to_ready상태여서 목적지가 정해진상태라
        # ready전까지 앞으로 나아감. 66, 69줄 약간 cnt로 바꿔서 5,4이렇게 해도됨. 1개씩 줄어들게      
def is_dest(robot_num):
    global robots
    global waiting_q, running_q
    if robots[robot_num]['now'] == robots[robot_num]['dest']: # 목적지에 도착했다면 
        # 1. [q] 상태 업데이트
        waiting_q.append(robots[robot_num]['num']) # waiting mode ON
        running_q.remove(robots[robot_num]['num']) # running mode OFF
        
        # 2. [robot] 상태 업데이트
        robots[robot_num]['status'] = 3 # WAITING
        
        # 새로운 목적지에 대한거 업데이트해줘야 함. ==> 사실은 이제 목적지가 없음 걍 waiting상태라는거 자체가 목적지임    
def status_chk():
    global robots
    READY = 1
    RUNNING = 2
    WAITING = 3
    
    for robot in range(1, robots): # 로봇들의 갯수만큼 반복 
        if robot['status'] == RUNNING: # 러닝중인 상태면 목적지에 도착했는지 확인
            # 도착했다면 waiting상태로 변경
            # 확인하는방법은 현재좌표랑 목적지좌표 비교
            if robot['dest'] == robot['now']: # 목적지에 도착함?
                # 그러면 상태를 바꿔주어야 함 run -> wait 
                
                # 전체 status 상태 업데이트
                waiting_q.append(robot['num']) # waiting mode ON
                running_q.remove(robot['num']) # running mode OFF
                
                # 그리고 로봇에게도 status를 알려주어야 함.
                
    # 현재위치와 목적지위치가 같은게 있냐 ==> 목적지에 도착한게 있냐?
    # 그러면 status를 running -> waiting으로 바꿔주어야 함.
    # 그래야 그자식의 다음목적지를 알려줄 수 있다...
def on_message(mqttc, userdata, message): # MQTT 클라이언트 객체에 콜백 함수 정의
    global info_1, info_2
    global real_message
    global cnt
    global ROBOT_NUM 
    global dests, robots
    global ready_q, running_q, packet_q
    RUNNING = 2
    WAITING = 3
    # print(f"수신된 메시지 수: {message_count}")
    # get_cooprdinate(str(message.payload.decode()))
    # message = str(message.payload.decode())
    real_message = str(message.payload.decode())
    
    if real_message[1] in packet_q: # 오지 않은 메시지에 한해서만 신호받기 
        packet_q.remove(real_message[1])
        
        # return message
        print("Received message: " + real_message)

        d = [] # ready에서 출발하는애 출발하는애는 무조건 앞으로 간다.
        
        # real_message[2] == 로봇의 번호
        if real_message[-1] == "d": # [ready]상태의 로봇 tag가 왔을 때
            print("[ready]로봇의 신호 도착 ==> 로봇번호: ", real_message[1])
            cnt += 1 
            print("cnt: ", cnt)
            
            # 로봇고유상태 업데이트
            robots[int(real_message[1])]['dest'] = "4" + real_message[2] # ex) 43 ==> 최종목적지 4,3
            robots[int(real_message[1])]['now']  = "1" + real_message[3] # ex) 12 ==> 현재위치 1,2
            
            # 1. [q] 상태 업데이트
            running_q.append(int(real_message[1])) # running mode ON 
            ready_q.remove(int(real_message[1])) # ready mode OFF 
            
            # 2.[robot] 상태 업데이트
            robots[int(real_message[1])]['status'] = 2 # RUNNING   

            d.append(int(real_message[1]))
            
        elif real_message[0] == '0': # [running, waiting]상태의 로봇의 신호가 왔을 때 
            cnt += 1
            print("cnt: ", cnt)
            print(real_message[1], "번 로봇 신호왔음", real_message[2:4], "좌표 도착하였습니다.")
            robots[int(real_message[1])]['now']  = real_message[2:4] # ex) 12, [running, waiting]상태이기에 최종목적지는 update하지 않는다.
            
            # 0123
            if robots[int(real_message[1])]['status'] == RUNNING: # running 상태라면 
                print("현재 [running]상태의 로봇입니다.")
                is_dest(int(real_message[1])) # 목적지에 도착했는지 확인 ==> 도착했다면 waiting 상태로 변경
            
            elif robots[int(real_message[1])]['status'] == WAITING: # running 상태라면 
                print("현재 [waiting]상태의 로봇입니다.")
                is_key_dest(int(real_message[1])) # key에 도착했는지 물어보기 
                is_dest_ready(int(real_message[1])) # ready상태까지 도착했는지 물어보는 함수 
        
        print("로봇1 위치: ", robots[1]['now'], "로봇2 위치: ", robots[2]['now'])
        if cnt == ROBOT_NUM: # cnt==2, 모두 좌표가 왔을 때  
            time.sleep(4)
            collision_alogrithm(d) # 충돌알고리즘 돌려서 다음목적지 전송 
            print("로봇들에게 충돌알고리즘을 통해서 좌표를 보냈습니다.")
            cnt = 0 # cnt갯수 초기화 
            packet_q = ["1","2"]
            d = []
            # print("로봇1좌표:", robots[1]['now'])
            # print("로봇2좌표:", robots[2]['now'])
            # info_1 = {'rec' : 1,'send' : 4, 'mtx_x' : robots[1]['now'][0], 'mtx_y' : robots[1]['now'][1] } # 형식을 json으로 변경
            # info_2 = {'rec' : 2,'send' : 4, 'mtx_x' : robots[2]['now'][0], 'mtx_y' : robots[2]['now'][1] } # 형식을 json으로 변경

    # a = message
    # return message
def wait_dest_decide(x, y):
    global robots
    
    if x==4 and (y>=1 and y<=5): # 무조건 +1
        return "4"+str(int(y)-1) # y+1해서 반납
    
    elif y==0 and (x>=2 and x<=4): # 아래로 이동 x--
        return str(int(x)-1)+"0"
    
    else: # 최종목적지 이동이라면
        return "1"+str(int(y)+1)    
def run_dest_decide(now_x, now_y, move_x, move_y): # 움직일 x좌표, 움직일 y좌표
    if abs(move_x) > abs(move_y): # x가 많이 남으면
        # 앞으로 무조건 전진
        next_hop_matrix =  str(int(now_x)+1) + now_y
        
    elif abs(move_x) <= abs(move_y): # y가 많이 남으면
        if move_y > 0: # 좌회전 
            y = int(now_y)+1
        else: # 우회전
            y = int(now_y)-1
        next_hop_matrix = now_x + str(y)
        
    # else: # 같으면 전진 ==> 근데 이때 0인경우 있냐? 없음 0,0 이여야 하는데 그럴일 없음 
    #     next_hop_matrix =  str(int(now_x)+1) + now_y
        
    return next_hop_matrix # "45" ==> (4,5) 
def collision_alogrithm(d): 
    global robots
    global running_q, waiting_q, ready_q
    
    ready_cnt = 0 # 1
    run_cnt = 0 # 2
    wait_cnt = 0 # 3
    
    # 1.로봇들의 따른 상태 찾기 
    for i in range(1,3): # 1~2
        if robots[i]['status'] == 1: # ready
            ready_cnt += 1
        elif robots[i]['status'] == 2:
            run_cnt += 1
        else:
            wait_cnt += 1
    
    # 2.충돌 알고리즘 설계
    if run_cnt == 2: # 1. run,run
        print("run상태의 2개의 로봇이 주행중입니다.")
        ip1 = robots[running_q[0]]['ip']
        ip2 = robots[running_q[1]]['ip']
        
        # ready상태에서 처음 출발하는 로봇은 앞으로 가야함.
        
        # robot 1
        now_run1_x = robots[running_q[0]]['now'][0]
        now_run1_y = robots[running_q[0]]['now'][1]
        dest_run1_x = robots[running_q[0]]['dest'][0]
        dest_run1_y = robots[running_q[0]]['dest'][1]
        move_x1 = int(dest_run1_x)-int(now_run1_x) # 움직일 x좌표 (1)
        move_y1 = int(dest_run1_y)-int(now_run1_y) # 움직일 y좌표 (1)
        next_move1 = run_dest_decide(now_run1_x, now_run1_y, move_x1, move_y1) # 로봇1의 다음 목적지
        
        # robot 2
        now_run2_x = robots[running_q[1]]['now'][0]
        now_run2_y = robots[running_q[1]]['now'][1]
        dest_run2_x = robots[running_q[1]]['dest'][0]
        dest_run2_y = robots[running_q[1]]['dest'][1]
        move_x2 = int(dest_run2_x)-int(now_run2_x) # 움직일 x좌표 (2)
        move_y2 = int(dest_run2_y)-int(now_run2_y) # 움직일 y좌표 (2)
        next_move2 = run_dest_decide(now_run2_x, now_run2_y, move_x2, move_y2) # 로봇2의 다음 목적지
        
        if now_run1_x=="1":
            next_move1 = 2 + now_run1_y
        if now_run2_x=="1":
            next_move2 = 2 + now_run2_y
        
        # 1번 충돌상황 == swap
        if (next_move1 == robots[running_q[1]]['now']) and (next_move2 == robots[running_q[0]]['now']): # swap 충돌
            # 로봇1 다음목적지 재정의 (뒤로빠꾸)
            print("swap충돌발생")
            next_move1 = str(int(now_run1_x)-1)+now_run1_y
        elif next_move1 == next_move2: # 2개의 목적지가 같을 경우
            # 한명이 대기 
            # 로봇1 다음목적지 재정의 (한턴쉬기)
            print("dest충돌발생")
            next_move1 = now_run1_x + now_run1_y
        else: # 충돌x
            pass
    
        # message 정의
        mes1 = str(running_q[0]) + "0" + next_move1
        mes2 = str(running_q[1]) + "0" + next_move2
               
        # 전달
        print("ip1: ", mes1, "을 보냅니다.")
        print("ip2: ", mes2, "을 보냅니다.")
        command1 = "mosquitto_pub -h {} -t dsTopic -m {}".format(ip1, mes1)
        command2 = "mosquitto_pub -h {} -t dsTopic -m {}".format(ip2, mes2)
        
        result2 = subprocess.run(command2, shell=True, capture_output=True) 
        time.sleep(1)
        result1 = subprocess.run(command1, shell=True, capture_output=True)
         
    elif wait_cnt == 2:
        
        # 무슨 로봇의 ip인줄은 모름 
        ip1 = robots[waiting_q[0]]['ip']
        ip2 = robots[waiting_q[1]]['ip']
        
        # 다음 목적지 계산
        next_dest1 = wait_dest_decide(int(robots[waiting_q[0]]['now'][0]), int(robots[waiting_q[0]]['now'][1])) # x,y
        next_dest2 = wait_dest_decide(int(robots[waiting_q[1]]['now'][0]), int(robots[waiting_q[1]]['now'][1])) # x,y
        
        # 패킷모양 만들기 
        mes1 = str(waiting_q[0]) + "0" + next_dest1
        mes2 = str(waiting_q[1]) + "0" + next_dest2
        
        # mes 만들기
        command1 = "mosquitto_pub -h {} -t dsTopic -m {}".format(ip1, mes1)
        command2 = "mosquitto_pub -h {} -t dsTopic -m {}".format(ip2, mes2)
        
        result1 = subprocess.run(command1, shell=True, capture_output=True)
        result2 = subprocess.run(command2, shell=True, capture_output=True)  
                
    elif ready_cnt == 2:
        
        ip1 = robots[ready_q[0]]['ip']
        ip2 = robots[ready_q[1]]['ip']
      
        # 패킷모양 만들기 
        mes1 = str(ready_q[0]) + "0" + robots[ready_q[0]]['now'] + "r"
        mes2 = str(ready_q[1]) + "0" + robots[ready_q[1]]['now'] + "r"
      
        # mes 만들기
        command1 = "mosquitto_pub -h {} -t dsTopic -m {}".format(ip1, mes1)
        command2 = "mosquitto_pub -h {} -t dsTopic -m {}".format(ip2, mes2)
      
        result1 = subprocess.run(command1, shell=True, capture_output=True)
        result2 = subprocess.run(command2, shell=True, capture_output=True)      
    elif run_cnt==1 and wait_cnt==1:
        # run이 우선순위이기 때문에 충돌이 발생하든 안하든 다음목적지 이동
        # wait은 충돌발생상황이라면 멈추기, 아니면 나아가기
        
        run_dest = robots[running_q[0]]['dest'] # 최종목적지
        now_wait_x = int(robots[waiting_q[0]]['now'][0])
        now_wait_y = int(robots[waiting_q[0]]['now'][1])
        
        # run robot 분석
        now_run_x = robots[running_q[0]]['now'][0]
        now_run_y = robots[running_q[0]]['now'][1]
        dest_run_x = robots[running_q[0]]['dest'][0]
        dest_run_y = robots[running_q[0]]['dest'][1]
        
        move_x = int(dest_run_x)-int(now_run_x) # 움직일 x좌표
        move_y = int(dest_run_y)-int(now_run_y) # 움직일 y좌표
        
        run_move = run_dest_decide(now_run_x, now_run_y, move_x, move_y) # 다음 움직 일 좌표
        
        run_ip = robots[running_q[0]]['ip']
        next_run_dest = str(running_q[0]) + "0" + run_move
        
        if now_run_x=="1":
            next_move1 = "2" + now_run_y
        
        command_run = "mosquitto_pub -h {} -t dsTopic -m {}".format(run_ip, next_run_dest)
        result_run = subprocess.run(command_run, shell=True, capture_output=True)
        
        wait_ip = robots[waiting_q[0]]['ip']
        # 충돌발생상황
        if run_dest == wait_dest_decide(now_wait_x, now_wait_y) and run_move == "10": # 최종목적지와 wait목적지가 같고 움직이는 로봇 앞으로 한칸이라면
            # 런닝상태가 우선순위 있다. ==> waiting은 한번 쉬기 
            next_wait_dest = str(waiting_q[0]) + "0" + robots[waiting_q[0]]['now'] # waiting은 현재좌표 그대로 전달
        else: # 충돌x ==> 둘 다 앞으로 한칸
            next_wait_dest = str(waiting_q[0]) + "0" + wait_dest_decide(now_wait_x, now_wait_y)
            
        command_wait = "mosquitto_pub -h {} -t dsTopic -m {}".format(wait_ip, next_wait_dest)
        result_wait = subprocess.run(command_wait, shell=True, capture_output=True)     
    elif wait_cnt==1 and ready_cnt==1:
        
        # waiting 로봇 좌표 전달
        ip = robots[waiting_q[0]]['ip']
        now_x = int(robots[waiting_q[0]]['now'][0])
        now_y = int(robots[waiting_q[0]]['now'][1])
        
        next_dest = str(waiting_q[0]) + "0" + wait_dest_decide(now_x, now_y)
        command = "mosquitto_pub -h {} -t dsTopic -m {}".format(ip, next_dest)
        result = subprocess.run(command, shell=True, capture_output=True)
        
        # ready 로봇 좌표 전달
        ip1 = robots[ready_q[0]]['ip']
        mes1 = str(ready_q[0]) + "0" + robots[ready_q[0]]['now'] + "r"
        command1 = "mosquitto_pub -h {} -t dsTopic -m {}".format(ip1, mes1)
        result1 = subprocess.run(command1, shell=True, capture_output=True)      
        
    elif ready_cnt==1 and run_cnt==1:
        # run 로봇 좌표 전달
        ip = robots[running_q[0]]['ip']
        now_x = robots[running_q[0]]['now'][0]
        now_y = robots[running_q[0]]['now'][1]
        dest_x = robots[running_q[0]]['dest'][0]
        dest_y = robots[running_q[0]]['dest'][1]
        
        move_x = int(dest_x)-int(now_x) # 움직일 x좌표
        move_y = int(dest_y)-int(now_y) # 움직일 y좌표 
        
        prefix =  str(running_q[0]) + "0"# 서버가 로봇번호에게 ==> 고정
        next_hop_mes = prefix + run_dest_decide(now_x, now_y, move_x, move_y) # 더 많이 남은거 먼저 없애기
        
        if now_x=="1":
            next_move1 = "2" + now_y
        
        command = "mosquitto_pub -h {} -t dsTopic -m {}".format(ip, next_hop_mes)
        result = subprocess.run(command, shell=True, capture_output=True)
                 
        
        # ready 로봇 좌표 전달
        ip1 = robots[ready_q[0]]['ip']
        mes1 = str(ready_q[0]) + "0" + robots[ready_q[0]]['now'] + "r"
        
        
        command1 = "mosquitto_pub -h {} -t dsTopic -m {}".format(ip1, mes1)
        result1 = subprocess.run(command1, shell=True, capture_output=True)
        
if __name__ == "__main__": 
    ROBOT_NUM = 2 # 배달로봇 갯수
    cnt = 0 # 모든 로봇 신호 전부 와야 다음 알고리즘 계산
    
    packet_q = ["1","2"]
    ready_q = [1,2] # 시작 시 1,2로봇 들어가 있음.
    running_q = [] 
    waiting_q = []
    
    info_1 = None
    info_2 = None
    
    #초깃값: {최종위치, 현재위치}
    # 3개의 status: 1,2,3 ==> ready, running, waiting
    robots = [{}, {"num":1, "dest":"", "now":"11", "status":1, "waitdest":"", "ip":"192.168.137.35"}, 
                  {"num":2, "dest":"", "now":"12", "status":1, "waitdest":"", "ip":"192.168.137.73"}]
    
    # mqtt 클라이언트를 별도의 쓰레드에서 실행
    mqtt_thread = threading.Thread(target=start_mqtt_client)
    mqtt_thread.start()
    
    app.run(debug=True)
    # app.run(host="0,0,0,0")
