# Init: 1s = 30 Frame
# Save image format: .jpg
# Save video format: .avi

import cv2
import socket
import datetime

import numpy as np

# 소켓 초기화
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Test를 위해서 로컬로 설정
sock.connect(('127.0.0.1', 12345))

# 카메라 초기화
camera = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'XVID')

# frame 확인을 위해 cnt
cnt = 0
# 녹화 중인지를 확인
record = False
# 사람이 연속으로 감지 되었는지 왁인
human = 0

while True:
    try:
        # 카메라 읽기
        grabbed, frame = camera.read()
        if record == True:
            # 녹화 중이면 매 프레임 마다 저장
            video.write(frame)
        # 카메라 640, 480 사이즈로 변경
        frame_ = cv2.resize(frame, (640, 480))

        # 1초 마다 사진 서버로 보내기
        if cnt >= 30:
            # Image encoding
            encoded, buffer = cv2.imencode('.jpg', frame_)

            # Array 변환
            data = np.array(buffer)
            # 문자열로 변환
            stringData = data.tostring()
            # encoding 작업 후 소켓 전송
            sock.send((str(len(stringData))).encode().ljust(16) + stringData)
            # 보낸 사진을 서버에서 판별 후 사람이 있는지를 알려줌
            value = sock.recv(10)

            # 'b'를 받으면 사람이 있다는 것, 'a'를 받으면 사람이 없다는 것

            # 사람이 없고 녹화중일 때
            if not 'b' in value.decode() and record == True:

                # 사람이 없을 때 1 추가(1초에 한번씩)
                human += 1
                # 4초 동안 사람이 없을 때
                if human >= 4:
                    # 녹화 종료
                    record = False
                    # video 저장
                    video.release()
                    print("Save video")
                    # human 초기화
                    human = 0
            else:
                # 사람이 다시 인식되면 0으로 초기화
                human = 0

            # 사람 감지 되고 영상을 녹화중이지 않을 때
            if "b" in value.decode() and record == False:
                # 저장할 파일 이름을 위해서 현재 날짜 불러오기
                now = datetime.datetime.now().strftime('%d_%H-%M-%S')
                # 영상 녹화 시작
                video = cv2.VideoWriter("./save/avi/" + str(now) + ".avi", fourcc, 30.0,
                                        (frame.shape[1], frame.shape[0]))
                # 녹화중으로 설정
                record = True

            # 1s 초기화
            cnt = 0
        else:
            # 1/30s 증가
            cnt += 1

        # 카메라 보여주기
        cv2.imshow('Frame', frame)

        # 키보드 입력
        c = cv2.waitKey(1)

        # 'a' 입력
        if c == ord('a'):
            # 녹화중일 때
            if (record == True):
                # 이미 녹화중이라고 알려주기
                print('Already recording')
            else:
                # 녹화 시작
                print('Start recording')
                # 저장할 파일 이름을 위해서 현재 날짜 불러오기
                now = datetime.datetime.now().strftime('%d_%H-%M-%S')
                # 영상 녹화 시작
                video = cv2.VideoWriter('./save/avi/' + str(now) + '.avi', fourcc, 30.0,
                                        (frame.shape[1], frame.shape[0]))
                record = True
        # 's' 입력
        if c == ord('s'):
            # 녹화 종료
            record = False
            # 녹화 저장
            video.release()
            print('Save Video')
            # 카운트 초기화
            human = 0
        # 'd' 입력
        if c == ord('d'):
            # 저장할 파일 이름을 위해서 현재 날짜 가져오기
            now = datetime.datetime.now().strftime('%d_%H-%M-%S')
            # 사진 저장
            cv2.imwrite('./save/png/' + str(now) + '.jpg', frame)
            print('Save Image')
        # 'q' 입력
        if c == ord('q'):
            print('End')
            # 종료
            break

        cv2.waitKey(1)
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        break
