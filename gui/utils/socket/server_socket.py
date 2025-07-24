import socket
import threading
import yaml
import json
from utils.network import get_my_ip

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
    server_socket_ip = get_my_ip()  # Use the local IP address
    server_socket_port = config.get("SERVER_SOCKET_PORT", 5000)

class ServerSocket:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, ip=server_socket_ip, port=server_socket_port):
        if not ServerSocket._initialized:
            super().__init__()
            self._init_state(ip, port)
            ServerSocket._initialized = True

    def _init_state(self, ip, port):
        self.ip = ip
        self.port = port    
        self.callbacks = []
        self.start()

    def add_callback(self, callback):
        if callable(callback):
            self.callbacks.append(callback)
        else:
            raise ValueError("Callback must be a callable function")

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip, self.port))
            s.listen(5)

            while True:
                conn, addr = s.accept()
                print(f"[ServerSocket] Connection from {addr}")
                with conn:
                    buffer = b""
                    while True:
                        chunk = conn.recv(1024)
                        if not chunk:
                            break
                        buffer += chunk
                        if b"\n" in buffer:
                            break  # 메시지 완성

                    try:
                        raw_msg = buffer.decode("utf-8").strip()
                        parsed_json = json.loads(raw_msg)
                        for callback in self.callbacks:
                            callback(parsed_json)
                    except Exception as e:
                        print(f"[ServerSocket] Error: {e}")

                    conn.sendall(b"Data received")