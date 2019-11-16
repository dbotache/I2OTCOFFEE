# !/usr/bin/env python
import socket

TCP_IP = '10.12.1.189'
TCP_PORT = 8585

BUFFER_SIZE = 1024

MESSAGE = 'KAFFEE_1'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((TCP_IP, TCP_PORT))

b = bytes(MESSAGE, 'utf-8')
s.send(b)

data = s.recv(BUFFER_SIZE)

s.close()

print("received data:", data)