import socket
import cv2
import pickle
import struct
import numpy as np
import face_recognition
import os
import logging


logging.basicConfig(level = "DEBUG", filename = "server.log", format='%(asctime)s-%(levelname)s-%(filename)s-%(message)s', datefmt='%d-%b-%y %H:%M:%S')
loger = logging.getLogger()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "0.0.0.0"
port = 9999

socket_address = (host, port)
server_socket.bind(socket_address)

server_socket.listen(5)
# print("LISTENING AT: ", socket_address)
loger.debug(f"LISTENING AT: {socket_address}")



path = 'knowsFaces'
images = []
classNames = []
myList = os.listdir(path)



for cls in myList:
    curImg = cv2.imread(f'{path}/{cls}')
    images.append(curImg)
    classNames.append(os.path.splitext(cls)[0])





def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


encodeListKnow = findEncodings(images)

print("Декодирование завершено!")




client_socket, addr = server_socket.accept()
while True:
    if client_socket:
        bufSize = 1024 * 1024
        image_buf = client_socket.recv(bufSize)
        loger.debug("Пакеты приняты сервером")

        data = np.frombuffer(image_buf, np.uint8)
        frame = cv2.imdecode(data, cv2.IMREAD_COLOR)

        imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodeCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnow, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnow, encodeFace)
            matchIndex = np.argmin(faceDis)
            name = 'Unknown'

            if matches[matchIndex]:
                name = classNames[matchIndex]
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)


            else:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)


        data = pickle.dumps(frame)
        client_socket.sendall(struct.pack("=L", len(data)) + data)
        loger.debug("Пакеты отправлены клиенту")

    else:
        break