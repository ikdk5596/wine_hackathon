import json
import socket
import struct

class ClientSocket:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

    # def send(self, data: dict):
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #         s.connect((self.ip, self.port))
    #         msg = json.dumps(data) + "\n"
    #         s.sendall(msg.encode("utf-8"))
    #         s.close()

    def send(self, json_dict, binary_bytes=None, binary_type=None):
        # 바이너리 여부에 따라 JSON 확장
        if binary_bytes is not None:
            json_dict["has_binary"] = True
            json_dict["binary_length"] = len(binary_bytes)
            json_dict["binary_type"] = binary_type
        else:
            json_dict["has_binary"] = False

        # JSON 직렬화
        json_bytes = json.dumps(json_dict).encode("utf-8")
        json_len = struct.pack("!I", len(json_bytes))

        # print("[Client] Sending data to server...", json_dict, 
        #       f"{'with binary data' if binary_bytes else 'without binary data'}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, self.port))
            s.sendall(json_len + json_bytes)
            if binary_bytes:
                s.sendall(binary_bytes)
