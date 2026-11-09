import socket

class Sender(object):
    s = None
    def __init__(self):
        global s
        TCP_IP = '127.0.0.1'  # historical example; configure for your board
        TCP_PORT = 8585
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))

    def send(self, message):
        if (s != None):
            b = bytes(message, 'utf-8')
            s.send(b)
            return True
        else:
            print("The Socket is None")
            return False