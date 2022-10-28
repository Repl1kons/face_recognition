import pickle
import socket
import struct

import cv2
import numpy as np
import threading
import logging

logging.basicConfig(level = "DEBUG", filename = "client.log", format='%(asctime)s-%(levelname)s-%(filename)s-%(message)s', datefmt='%d-%b-%y %H:%M:%S')
loger = logging.getLogger()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "localhost"
port = 9999
addc = (host, port)
try:
    client_socket.connect(addc)
    loger.debug("Подключение установлено")

except Exception as ex:
    loger.debug(f"Подключение не было установлено по ошибке {ex}")

cap = cv2.VideoCapture(0)
quality = 30  # Качество изображения
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]

def sender():
    while True:
        try:
            ret, frame_send = cap.read()
            if not ret:
                break

            frame_send = cv2.flip(frame_send, 1)
            cv2.imshow('send_on_server', frame_send)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            img_encode = cv2.imencode(".jpg", frame_send, encode_param)[1]
            data_encode = np.array(img_encode)
            str_encode = data_encode.tobytes()
            client_socket.sendto(str_encode, addc)
            loger.debug("Пакеты отправлены на сервер")
        except Exception as ex:
            loger.debug(f"Пакеты не были отправлены на сервер по причине {ex}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        print(fps)

def reciver():
    while True:
        try:
            data = b''
            payload_size = struct.calcsize("=L")
            while len(data) < payload_size:
                data += client_socket.recv(1024 * 1024)
            packed_msg_size = data[:payload_size]

            data = data[payload_size:]
            msg_size = struct.unpack("=L", packed_msg_size)[0]
            loger.debug("Пакеты приняты с сервера и распакованы ")

            while len(data) < msg_size:
                data += client_socket.recv(1024 * 1024)
            frame_data = data[:msg_size]
            frame_img = pickle.loads(frame_data)

            cv2.imshow('client', frame_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except Exception as ex:
            loger.debug(f"Ошибка: {ex}")

send = threading.Thread(target = sender).start()
reciveThreading = threading.Thread(target = reciver).start()