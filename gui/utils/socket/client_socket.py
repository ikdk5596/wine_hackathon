import socket

class ClientSocket:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

    def send(self, data: bytes):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, self.port))
            s.sendall(data)
            s.close()
        
