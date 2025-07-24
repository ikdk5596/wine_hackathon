import json
import socket

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
    # server_socket_port = config.get("SERVER_SOCKET_PORT", 5000)
    server_socket_port = 6000  # Default port if not specified in config

class ClientSocket:
    def __init__(self, ip: str):
        self.ip = ip
        self.port = server_socket_port

    def send(self, data: dict):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, self.port))
            msg = json.dumps(data) + "\n"
            s.sendall(msg.encode("utf-8"))
            s.close()
        
