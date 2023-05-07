[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fhttps%2F%2Fgithub.com%2Fsoftwareyong%2FCapstone-Design%2Fhit-counter&count_bg=%23C83D8F&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://github.com/softwareyong/Capstone-Design)

# Capstone-Design
> qr tag를 이용하여 로봇이 좌표를 서버로 전달하며

> 서버가 다음 목적지를 주며 최종목적지로 배달을 진행하는 서비스

## 🕰️개발 기간 
> 2023.03.02 ~ 2023.06(~ing) 전자공학과 캡스톤 프로젝트

## 🧑‍🤝‍🧑 조원 소개
>  이용우(PL), 박현수, 홍성호, 김지욱

### ⚙️ 개발 환경
- `python 3.8.x`
-  rasberry pi: v1.7.3
- **IDE** : vs code
- **Framework** : flask
- **tools** : VNC Viewer, xftp7, xshell7
- 모스키토버전, 최종로봇, 최종맵, 모니터링서비스화면, 코드update, 추가해야함

# 2. 배경 및 목적
* 현대의 물류센터는 처리해야 하는 물류량이 정말 많아서 직원이 정말 많이 필요합니다.
물류센터의 비정규직은 거의 95%에 육박합니다.
그에 비해 물류센터는 냉난방시스템 등 근무환경이 매우 열약합니다.
그에 따라 미흡한 근무환경과 관리되지않는 업무로 과로사, 감전사고등 안타깝게도
최근까지 사고가 일어나고 있는게 현실입니다.
그래서 현대의 선진국 물류센터들과 쿠팡등 자동화시스템을 구축하여 이런 문제를 해결합니다.
![image](https://user-images.githubusercontent.com/95459741/236624434-f6356f26-a575-499d-a50c-e1e812bc2a3d.png)
이에 일부분을 재현하고 물류서비스의 생산성 및 안정성을 개선해보는데 목표를 둔다.

# 3. 주요 서비스 화면
> 토글 클릭하시면 이미지 확인이 가능합니다.
<details>
  <summary>실제 map</summary>
  
![KakaoTalk_20230506_214425609](https://user-images.githubusercontent.com/95459741/236626064-6fc66a95-2664-4801-8a64-a7615631d049.jpg)


</details>

<details>
  <summary>최종 로봇</summary>
  
 </details>
 
# 4. 로봇 version 업데이트
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

</details>
  
# System flow
![image](https://user-images.githubusercontent.com/95459741/236448976-7e4114fc-41d0-441c-ad70-0887a09ffd33.png)

