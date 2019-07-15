# embedded_project_2019
## 개요
어떤 사건에 발생해서 CCTV로 녹화된 사람 찾아야할 때 사람이 직접 눈으로 확인하면서 녹화된 영상을 확인하기란 쉽지 않다. 그래서 CCTV에 사람이 찍힐 때만 영상이 저장되도록 만드는 것이 목적이다.

## 구조
![](https://github.com/Yudonggeun/embedded_project_2019/blob/master/image/structure.png)
YOLOv3 Model이 라즈베리파이에 올리기 힘들어서 client와 server의 통신이 필요햔다.
 
작동 순서
    1. client에서는 사진을 전송한다.
    3. server의 YOLOv3가 사람을 감지한다.
    4. server에서 감지 결과를 client로 전송한다.
    5. server에서 사람이 감지되었다고 보내주었을 때 영상 촬영을 시작하고 사람이 4초 동안 감지되지 않으면 영상을 저장한다.
    
## 실행 방법
다음 YOLOv3 Model를 다운 받아준다. [Qidian213's yolo.h5](https://drive.google.com/file/d/1uvXFacPnrSMw6ldWTyLLjGLETlEsUvcE/view) 이 파일을 './model_data/'에 복사한다.

client와 server의 하드웨어가 독립적이라면 ip주소를 설정해야한다.

server를 실행시킨다.
~~~
python3 server.py
~~~

'model_data/yolo.h5 model, anchors, and classes loaded.'가 출력 되면 YOLOv3 model과 socket이 준비가 된 것이다. 이 이후에 client를 실행시켜야 한다.
~~~
python3 client.py
~~~

단축키
    * a: 녹화 시작
    * s: 녹화 저장
    * d: 사진 저장
    
매우 실행이 잘 될 것이다.

### 실제 작동 모습
맥북을 서버로 사용하였고 서버에는 흰색 박스로 사람이 감지된다는 것을 알려준다.
![](https://github.com/Yudonggeun/embedded_project_2019/blob/master/image/communication.JPG)

## 실험
가벼운 OpenCV와 비교를 위해서 실험을 진행하였다. OpenCV는 'haarcascade_fullbody.xml'를 사용하였다. 하얀색 박스가 YOLOv3이고 검은색 박스가 OpenCV이다.
왼쪽 사진의 경우 소화기 표시가 사람 몸으로 인식되었다. 오른쪽 사진은 책장 쪽이 사람 몸으로 인식되는 것을 확인할 수 있었다.
![](https://github.com/Yudonggeun/embedded_project_2019/blob/master/image/demo.png)

### 직접 테스트
demo를 통해서 직접 비교해볼 수 있다. 통신이 아닌 한 컴퓨터에서만 가능하다.
~~~
python3 demo.py
~~~

## Reference
YOLOv3 Human detection: [Qidian213/deep_sort_yolov3](https://github.com/Qidian213/deep_sort_yolov3)