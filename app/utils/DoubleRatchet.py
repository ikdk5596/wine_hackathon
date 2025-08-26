import os
import hmac
import hashlib
import json
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class DoubleRatchet:
    def __init__(self, root_key: bytes, dh_priv: bytes, dh_pub_remote: bytes):
        self.root_key = root_key
        self.dh_priv = dh_priv
        self.dh_pub = self._derive_pub(dh_priv)
        self.dh_pub_remote = dh_pub_remote

        self.send_chain_key = root_key
        self.recv_chain_key = root_key
        self.send_count = 0
        self.recv_count = 0

    def _derive_pub(self, priv: bytes) -> bytes:
        if not isinstance(priv, bytes):
            raise TypeError("Private key must be bytes")
        return hashlib.sha256(priv).digest()

    def _dh(self, priv: bytes, pub: bytes) -> bytes:
        if not isinstance(priv, bytes) or not isinstance(pub, bytes):
            raise TypeError("DH inputs must be bytes")
        return hashlib.sha256(priv + pub).digest()

    def _kdf_chain(self, chain_key: bytes) -> tuple:
        new_chain_key = hmac.new(chain_key, b"chain", hashlib.sha256).digest()
        msg_key = hmac.new(chain_key, b"msg", hashlib.sha256).digest()[:32]
        return new_chain_key, msg_key

    def _ratchet(self):
        self.dh_priv = os.urandom(32)
        self.dh_pub = self._derive_pub(self.dh_priv)
        shared_secret = self._dh(self.dh_priv, self.dh_pub_remote)
        self.root_key = hashlib.sha256(self.root_key + shared_secret).digest()
        self.send_chain_key = self.root_key
        self.send_count = 0

    def encrypt(self, plaintext: bytes) -> dict:
        if self.send_count > 0 and self.send_count % 20 == 0:
            self._ratchet()

        self.send_chain_key, msg_key = self._kdf_chain(self.send_chain_key)
        nonce = os.urandom(12)
        aesgcm = AESGCM(msg_key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        self.send_count += 1

        def encode(b): return b64encode(b).decode()

        return json.dumps({
            "ciphertext": encode(ciphertext),
            "nonce": encode(nonce),
            "header": {
                "dh_pub": encode(self.dh_pub),
                "msg_num": self.send_count
            }
        })


    def decrypt(self, json_str: dict) -> bytes:
        def decode(s): return b64decode(s.encode())

        message = json.loads(json_str)

        if message["header"]["msg_num"] > 0 and message["header"]["msg_num"] % 20 == 0:
            self.dh_pub_remote = decode(message["header"]["dh_pub"])
            shared_secret = self._dh(self.dh_priv, self.dh_pub_remote)
            self.root_key = hashlib.sha256(self.root_key + shared_secret).digest()
            self.recv_chain_key = self.root_key
            self.recv_count = 0

        self.recv_chain_key, msg_key = self._kdf_chain(self.recv_chain_key)
        aesgcm = AESGCM(msg_key)
        plaintext = aesgcm.decrypt(
            decode(message["nonce"]),
            decode(message["ciphertext"]),
            None
        )
        self.recv_count += 1
        return plaintext


    def to_json(self) -> str:
        def encode(b):
            if isinstance(b, str):
                b = b.encode()
            return b64encode(b).decode()

        return json.dumps({
            "root_key": encode(self.root_key),
            "dh_priv": encode(self.dh_priv),
            "dh_pub": encode(self.dh_pub),
            "dh_pub_remote": encode(self.dh_pub_remote),
            "send_chain_key": encode(self.send_chain_key),
            "recv_chain_key": encode(self.recv_chain_key),
            "send_count": self.send_count,
            "recv_count": self.recv_count
        })

    @staticmethod
    def from_json(json_str: str):
        def decode(s):
            return b64decode(s.encode())

        data = json.loads(json_str)
        obj = DoubleRatchet(
            root_key=decode(data["root_key"]),
            dh_priv=decode(data["dh_priv"]),
            dh_pub_remote=decode(data["dh_pub_remote"])
        )
        obj.dh_pub = decode(data["dh_pub"])
        obj.send_chain_key = decode(data["send_chain_key"])
        obj.recv_chain_key = decode(data["recv_chain_key"])
        obj.send_count = data["send_count"]
        obj.recv_count = data["recv_count"]
        return obj