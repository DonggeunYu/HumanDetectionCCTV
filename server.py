import cv2
import os
import numpy as np
from PIL import Image
from yolo import YOLO
import socket

os.environ['OPENCV_IO_MAX_IMAGE_PIXELS']=str(2**64)

from deep_sort import preprocessing
from deep_sort import nn_matching
from deep_sort.detection import Detection
from deep_sort.tracker import Tracker
from tools import generate_detections as gdet

max_cosine_distance = 0.3
nms_max_overlap = 1.0


fourcc = cv2.VideoWriter_fourcc(*'XVID')

nn_budget = None
# YOLO Model 불러오
model_filename = 'model_data/mars-small128.pb'
encoder = gdet.create_box_encoder(model_filename, batch_size=1)

# YOLO 설
metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
tracker = Tracker(metric)
yolo = YOLO()
fps = 0.0

# socket 설정
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', 12345))
server_socket.listen(1)
client_socket, addr = server_socket.accept()

def recvall(sock, count):
    # 바이트 문자열
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

while True:
        # 처음 buf는 사진 길이를 저장함.
        length = recvall(client_socket, 16)
        # 사진 길이만큼 뒤에서 잘라서 받기
        stringData = recvall(client_socket, int(length))
        # uint8
        frame = np.fromstring(stringData, dtype='uint8')

        # cv2로 encoding
        source = cv2.imdecode(frame, 1)
        # 전송이 오류 없이 성공적으로 도착했을 때.
        if str(type(source)) == "<class 'numpy.ndarray'>":
            # 잘 밧았다고 1 보내주기
            client_socket.send(bytearray("1", 'utf=8'))

            # bgr to rgb
            image = Image.fromarray(source[..., ::-1])
            # model에 사진 넣기
            boxs = yolo.detect_image(image)
            # print("box_num",len(boxs))
            features = encoder(source, boxs)

            # score to 1.0 here).
            detections = [Detection(bbox, 1.0, feature) for bbox, feature in zip(boxs, features)]

            # Run non-maxima suppression.
            boxes = np.array([d.tlwh for d in detections])
            scores = np.array([d.confidence for d in detections])
            indices = preprocessing.non_max_suppression(boxes, nms_max_overlap, scores)
            detections = [detections[i] for i in indices]

            # Call the tracker
            tracker.predict()
            tracker.update(detections)

            for track in tracker.tracks:
                if not track.is_confirmed() or track.time_since_update > 1:
                    continue
                bbox = track.to_tlbr()
                # 사람 위치 Box로 표시하기
                cv2.rectangle(source, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255, 255, 255), 2)
                # cv2.putText(frame, str(track.track_id),(int(bbox[0]), int(bbox[1])),0, 5e-3 * 200, (0,255,0),2)
                # 사람이 1명보다 많다고 인식 될 때
                if len(np.shape(boxes)) > 1:
                    print('human')
                    # 'b' 보내기
                    client_socket.send(bytearray("b", 'utf=8'))
            # cv2로 영상 출력
            cv2.imshow('', source)

        # 기본적으로 'a' 보내기
        client_socket.send(bytearray("a", 'utf=8'))
        cv2.waitKey(1)
