import socket
import threading

class ServerSocket:
    def __init__(self, ip: str, port: int, callback=None):
        self.ip = ip
        self.port = port
        self._callback = callback

    def on_receive(self, callback):
        """Register callback that accepts raw `bytes`"""
        self._callback = callback

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip, self.port))
            s.listen(1)
            print(f"[ServerSocket] Listening on {self.ip}:{self.port}")
            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"[ServerSocket] Connected by {addr}")
                    data = b""
                    while True:
                        packet = conn.recv(4096)
                        if not packet:
                            break
                        data += packet
                    if self._callback:
                        self._callback(data)
