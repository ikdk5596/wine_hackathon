import json
import socket


class ClientSocket:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

    def send(self, data: dict):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, self.port))
            msg = json.dumps(data) + "\n"
            s.sendall(msg.encode("utf-8"))
            s.close()
        
