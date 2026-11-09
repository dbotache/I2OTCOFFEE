# pip install pyserial
from serial import *

class WireDriver:
    def __init__(self):
        self.ser = Serial()
        self.ser.baudrate = 9600
        self.ser.port = "/dev/ttyUSB0"
        self.ser.open()

    def send(self, text=""):
        self.ser.write(bytes(text.encode()))
        string = self.ser.readline()
        print(string)

    def __del__(self):
        self.ser.close()
