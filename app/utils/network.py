import yaml
import socket

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
    server_socket_port = config.get("SERVER_SOCKET_PORT", 5000)

def get_my_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "0.0.0.0"
    
def get_my_port():
    return server_socket_port