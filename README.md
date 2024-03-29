[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fhttps%2F%2Fgithub.com%2Fsoftwareyong%2FCapstone-Design%2Fhit-counter&count_bg=%23C83D8F&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://github.com/softwareyong/Capstone-Design)

# Capstone-Design
> qr tag를 이용하여 로봇이 좌표를 서버로 전달하며

> 서버가 다음 목적지를 주며 최종목적지로 배달을 진행하는 서비스

## 🕰️개발 기간 
> 2023.03.02 ~ 2023.06.20 전자공학과 캡스톤 프로젝트

## 🧑‍🤝‍🧑 조원 소개
>  이용우(PL), 박현수, 홍성호, 김지욱 

### ⚙️ 개발 환경
- `python 3.8.x`
-  rasberry pi: v1.7.3
- **IDE** : vs code
- **Framework** : flask
- **tools** : VNC Viewer, xftp7, xshell7
- **protocol** : MQTT(Msg broker=> Mosquitto)

# 2. 배경 및 목적
* 현시대의 물류센터는 상당량의 물류량을 처리해야 하기 때문에 다수의 직원이 필요합니다.

물류센터의 비정규직은 거의 95%에 육박합니다.
그에 비해 물류센터는 냉난방시스템 등 근무환경이 매우 열약합니다.
그에 따라 미흡한 근무환경과 관리되지않는 업무로 과로사, 감전사고등 안타깝게도
최근까지 사고가 일어나고 있는게 현실입니다.
그래서 현대의 선진국 물류센터들과 쿠팡등 자동화시스템을 구축하여 이런 문제를 해결합니다.
이에 일부분을 재현하고 물류서비스의 생산성 및 안정성을 개선해보는데 목표를 둔다.
![image](https://user-images.githubusercontent.com/95459741/236624434-f6356f26-a575-499d-a50c-e1e812bc2a3d.png)

# 주요기능
ㅁ 관리자가 로봇들의 현재 좌표를 볼 수 있는 실시간 모니터링 서비스

ㅁ 로봇이 충돌없이 목적지로 이동하여 택배를 배송하는 서비스

# 3. 주요 서비스 화면
> 토글 클릭하시면 이미지 확인이 가능합니다.
<details>
   <summary>Map</summary>
  
![최종맵](https://github.com/softwareyong/Capstone-Design/assets/95459741/0cc838c1-d4f6-437d-8cde-e887dd83ef79)

</details>

<details>
  <summary>Robot</summary>
   
  ![최종로봇](https://github.com/softwareyong/Capstone-Design/assets/95459741/da87bf89-eb2b-42af-a5d4-c00c526c2c35)
   
 </details>
 
 <details>
  <summary>실시간 모니터링 서비스</summary>
   
![실시간모니터링서비스사진](https://github.com/softwareyong/Capstone-Design/assets/95459741/fa6c4f90-9231-4bde-abf2-f24c9709d64e)

 </details>
 
# 4. Robot Ver.
 <details>
      <summary>로봇 ver1</summary>
  
![image01](https://user-images.githubusercontent.com/95459741/236626518-09afd51c-1f75-41ad-afcd-5a1949b58f33.jpg)


  <summary> <지면을 수직으로 바라보게 함> </summary>
  
  </details>
<details>
  <summary>로봇 ver2</summary>
   
![image](https://user-images.githubusercontent.com/95459741/236625188-d5d1ca8d-14af-4c1b-8eeb-bccf3c209ce4.png)
   
  <summary> 지면 수직 + 자체 높이 증가</summary>
      
</details>

 <details>
  <summary>로봇 ver3</summary>
   
![KakaoTalk_20230506_215340564](https://user-images.githubusercontent.com/95459741/236626614-c25c9d8e-71f9-45dc-8ec8-5f367f826174.jpg)
    
    
  <summary> < qr코드크기 최적화에 따른 자체 높이 다시 감소> </summary>
    
</details>

 <details>
  <summary>로봇 ver4</summary>
   
![ver4](https://github.com/softwareyong/Capstone-Design/assets/95459741/f71f0d75-0248-4d09-9f5b-84672fbe3785)
   
   <summary> <무게최소화, 무게중심 앞으로 변경> </summary>
</details>
    
  <details>
  <summary>로봇 ver5</summary>
  
  ![noname01](https://github.com/softwareyong/Capstone-Design/assets/95459741/18ae7bf0-987f-49de-8af1-0c0e68caf8aa)
![KakaoTalk_20230522_224626026](https://github.com/softwareyong/Capstone-Design/assets/95459741/3a35bcac-b3e4-4e83-9441-660492479add)


   <summary> 3D CAD로 카메라 거치대 자제 제작 </summary>
</details>
    
 <details>
  <summary>로봇 ver6_최종</summary>
    
  ![KakaoTalk_20230522_225032655](https://github.com/softwareyong/Capstone-Design/assets/95459741/fd623ffd-6d5e-4a19-be40-e08759604e61)

   <summary> 택배 운반장치 추가 </summary>
</details>
    
  
# System Flow
![image](https://user-images.githubusercontent.com/95459741/236448976-7e4114fc-41d0-441c-ad70-0887a09ffd33.png)

# FlowChart
![image](https://github.com/softwareyong/Capstone-Design/assets/95459741/cf357f1e-08bd-4f49-ae4b-96d2b63227e3)
    
# Status Cycle
![status](https://github.com/softwareyong/Capstone-Design/assets/95459741/9385f6df-a07a-4e3c-b733-01e60553ee0e)
