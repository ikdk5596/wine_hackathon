import socket
import struct
import threading
import yaml
import json
import numpy as np
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

    def _recv_exact(self, conn, n):
        buf = b""
        while len(buf) < n:
            chunk = conn.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("Connection closed prematurely")
            buf += chunk
        return buf

    def _run(self):
        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #     s.bind((self.ip, self.port))
        #     s.listen(5)

        #     while True:
        #         conn, addr = s.accept()
        #         print(f"[ServerSocket] Connection from {addr}")
        #         with conn:
        #             buffer = b""
        #             while True:
        #                 chunk = conn.recv(1024)
        #                 if not chunk:
        #                     break
        #                 buffer += chunk
        #                 if b"\n" in buffer:
        #                     break  # 메시지 완성

        #             try:
        #                 raw_msg = buffer.decode("utf-8").strip()
        #                 parsed_json = json.loads(raw_msg)
        #                 for callback in self.callbacks:
        #                     callback(parsed_json)
        #             except Exception as e:
        #                 print(f"[ServerSocket] Error: {e}")

        #             conn.sendall(b"Data received")

        #             def start_server(host="0.0.0.0", port=9999):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip, self.port))
            s.listen()

            while True:
                conn, addr = s.accept()
                with conn:
                    # print(f"[Server] Connection from {addr}")

                    # Json length
                    header = self._recv_exact(conn, 4)
                    json_len = struct.unpack("!I", header)[0]

                    # Json data
                    json_data = self._recv_exact(conn, json_len)
                    json_dict = json.loads(json_data.decode("utf-8"))

                    # Binary data
                    binary_data = None
                    binary_type = None
                    if json_dict.get("has_binary"):
                        binary_data = self._recv_exact(conn, json_dict["binary_length"])
                        binary_type = json_dict["binary_type"]
                        # print(f"[Server] Received binary ({binary_type}, {len(binary_data)} bytes)")

                    for callback in self.callbacks:
                        callback(json_dict, binary_data, binary_type)

                    # 4. 응답
                    conn.sendall(b"OK")