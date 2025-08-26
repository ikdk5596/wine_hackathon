import io
import base64
import random
import string
import numpy as np
from PIL import Image
from api import friend_api
from utils.network import get_my_ip, get_my_port
from utils.core.encryption import encrypt_with_RSAKey, decrypt_with_RSAKey
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from utils.DoubleRatchet import DoubleRatchet
from utils.socket.server_socket import ServerSocket
from utils.socket.client_socket import ClientSocket
from utils.image import base64_to_image, image_to_base64
from states.user_store import UserStore
from states.friends_store import FriendsStore, Friend

class FriendController:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        if not FriendController._initialized:
            super().__init__()
            self._init_state()
            FriendController._initialized = True 

    def _init_state(self):
        ServerSocket().add_callback(self._handle_socket_response)

    def add_friend(self, user_id: str, ip: str, port: int, friend_id: str, public_key: RSAPublicKey, profile_image: Image.Image | None, root_key: bytes) -> dict:
        if not isinstance(ip, str):
            raise ValueError("IP address must be a string")
        if not isinstance(port, int):
            raise ValueError("Port must be an integer")
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string")
        if not isinstance(friend_id, str):
            raise ValueError("Friend ID must be a string")
        if not isinstance(public_key, RSAPublicKey):
            raise ValueError("Public key must be a RSAPublicKey object")
        if not isinstance(profile_image, Image.Image | None):
            raise ValueError("Profile image must be a PIL Image object")
        
        userStore = UserStore()

        if not userStore.is_authenticated:
            return {
                "status": "error",
                "message": "User is not authenticated"
            }
        
        # Create key bytes
        priv_bytes = userStore.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        pub_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        doubleRatchet = DoubleRatchet(root_key, priv_bytes, pub_bytes)
        
        # Serialize
        public_key = pub_bytes.decode('utf-8')
        profile_base64 = image_to_base64(profile_image) if profile_image else None
        double_ratchet_info = doubleRatchet.to_json()

        response = friend_api.create_friend(user_id, ip, port, friend_id, public_key, profile_base64, double_ratchet_info)

        if response.get("status") == "success":
            data = response.get("data")

            # Deserialize profile image
            public_key = serialization.load_pem_public_key(data["public_key"].encode('utf-8'))
            profile_image = base64_to_image(data.get("profile_base64")) if data.get("profile_base64") else None

            # Update FriendsStore
            friend = Friend(
                user_id=data["user_id"],
                ip=data["ip"],
                port=data["port"],
                friend_id=data["friend_id"],
                public_key=public_key,
                profile_image=profile_image,
                messages_list=[],
                doubleRatchet = doubleRatchet
            )
            FriendsStore().add_friend(friend)            
            return {
                "status": response.get("status", "success"),
                "message": response.get("message", "Friend added successfully"),
            }
        else:
            return {
                "status": response.get("status", "error"),
                "message": response.get("message", "Failed to add friend")
            }
        
    def delete_friend(self, user_id: str, friend_id: str) -> dict:
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string")
        if not isinstance(friend_id, str):
            raise ValueError("Friend ID must be a string")
    
        if not UserStore().is_authenticated:
            return {
                "status": "error",
                "message": "User is not authenticated"
            }
        
        response = friend_api.delete_friend(user_id, friend_id)

        if response.get("status") == "success":
            FriendsStore().remove_friend(friend_id)
            return {
                "status": response.get("status", "success"),
                "message": response.get("message", "Friend deleted successfully"),
            }
        else:
            return {
                "status": response.get("status", "error"),
                "message": response.get("message", "Failed to delete friend")
            }
        
    def load_friends(self) -> dict:
        if not UserStore().is_authenticated:
            return {
                "status": "error",
                "message": "User is not authenticated"
            }

        response = friend_api.get_friends(UserStore().user_id)

        print(response)

        if response.get("status") == "success":
            data = response.get("data")
            
            # Deserialize friends
            friends_list = []
            for friend in data["friends"]:
                friend["public_key"] = serialization.load_pem_public_key(friend["public_key"].encode('utf-8'))
                friend["profile_image"] = base64_to_image(friend["profile_base64"])
                messages_list = []
                for message in friend["messages_list"]:
                    if message.get("text"):
                        messages_list.append({
                            "sender_id": message['sender_id'],
                            "text": message['text'],
                            "timestamp": message['timestamp'],
                            "is_read": message['is_read']
                        })
                        continue     
                    enc_seed_bytes = base64.b64decode(message["enc_seed_string"].encode('utf-8'))
                    messages_list.append({
                        "sender_id": message['sender_id'],
                        "enc_latent_size": message['enc_latent_size'],
                        "enc_latent_array": message['enc_latent_array'],
                        "enc_seed_bytes": enc_seed_bytes,
                        "seed_string": message['seed_string'],
                        "timestamp": message['timestamp'],
                        "is_read": message['is_read']
                    })
                doubleRatchet = DoubleRatchet.from_json(friend["double_ratchet_info"])
                friends_list.append(Friend(
                    user_id=friend["user_id"],
                    ip=friend["ip"],
                    port=friend["port"],
                    friend_id=friend["friend_id"],
                    public_key=friend["public_key"],
                    profile_image=friend["profile_image"],
                    messages_list= messages_list,
                    doubleRatchet=doubleRatchet
                ))
            
            # Update FriendsStore
            FriendsStore().friends_list = friends_list

            return {
                "status": "success",
                "message": "Friends loaded successfully"
            }
        else:
            return {
                "status": "error",
                "message": response.get("message", "Failed to load friends")
            }

    def request_friend(self, ip: str, port: int) -> dict:
        if not isinstance(ip, str):
            raise ValueError("IP address must be a string")
        if not isinstance(port, int):
            raise ValueError("Port must be an integer")
        
        userStore = UserStore()
        if not userStore.is_authenticated:
            return {
                "status": "error",
                "message": "User is not authenticated"
            }
        
        # Serialize
        public_key = userStore.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        profile_base64 = image_to_base64(userStore.profile_image)

        # Send request
        request_socket = ClientSocket(ip, port)
        request_socket.send({
            "type": "request_friend",
            "data": {
                "ip": get_my_ip(),
                "port": get_my_port(),
                "user_id": userStore.user_id,
                "public_key": public_key,
                "profile_base64": profile_base64 if userStore.profile_image else None,
                }
            })

        return {
            "status": "success",
            "message": "Friend request sent successfully"
        }
    
    def receive_text_message(self, friend_id: str, dr_message: str, timestamp: float) -> None:
        userStore = UserStore()
        if not userStore.is_authenticated:
            return {
                "status": "error",
                "message": "User is not authenticated"
            }
        
        friendStore = FriendsStore()
        friend = friendStore.get_friend(friend_id)
        if not friend:
            return {
                "status": "error",
                "message": "Friend not found"
            }
        
        text = friend.doubleRatchet.decrypt(dr_message)
        double_ratchet_info = friend.doubleRatchet.to_json()
        is_read = friendStore.selected_friend and friendStore.selected_friend.friend_id == friend_id
        response = friend_api.create_text_message(userStore.user_id, friend_id, friend_id, text, double_ratchet_info,
                                             timestamp=timestamp, is_read=is_read)

        if response.get("status") == "success":
            data = response.get("data")

            # Update FriendsStore
            message = {
                "sender_id": data['sender_id'],
                "text": data['text'],
                "timestamp": data['timestamp'],
                "is_read": data['is_read']
            }
            friend.messages_list = [*friend.messages_list, message]
            
            return {
                "status": response.get("status", "success"),
                "message": response.get("message", "Message sent successfully"),
            }
        
        else:
            return {
                "status": response.get("status", "error"),
                "message": response.get("message", "Failed to send message")
            }

    def receive_latent_message(self, friend_id: str,  enc_latent_size: int, enc_latent_array: np.ndarray, enc_seed_string: str, seed_string: str, timestamp: float) -> None:
        userStore = UserStore()
        if not userStore.is_authenticated:
            return {
                "status": "error",
                "message": "User is not authenticated"
            }
        
        friendStore = FriendsStore()
        friend = friendStore.get_friend(friend_id)
        if not friend:
            return {
                "status": "error",
                "message": "Friend not found"
            }
        
        is_read = friendStore.selected_friend and friendStore.selected_friend.friend_id == friend_id
        response = friend_api.create_latent_message(userStore.user_id, friend_id, friend_id, enc_latent_size,
                                                enc_latent_array, enc_seed_string, seed_string,
                                                timestamp=timestamp, is_read=is_read)

        if response.get("status") == "success":
            data = response.get("data")

            # Update FriendsStore
            enc_seed_bytes = base64.b64decode(enc_seed_string.encode('utf-8'))
            message = {
                "sender_id": data['sender_id'],
                "enc_latent_array": enc_latent_array,
                "enc_latent_size": data['enc_latent_size'],
                "enc_seed_bytes": enc_seed_bytes,
                "seed_string": data['seed_string'],
                "timestamp": data['timestamp'],
                "is_read": data['is_read']
            }
            friend.messages_list = [*friend.messages_list, message]
            
            return {
                "status": response.get("status", "success"),
                "message": response.get("message", "Message sent successfully"),
            }
        
        else:
            return {
                "status": response.get("status", "error"),
                "message": response.get("message", "Failed to send message")
            }
        
    def select_friend(self, friend_id: str) -> None:
        if not isinstance(friend_id, str):
            raise ValueError("Friend ID must be a string")
            
        userStore = UserStore()
        if not userStore.is_authenticated:
            return {
                "status": "error",
                "message": "User is not authenticated"
            }
        
        friendStore = FriendsStore()
        friend = friendStore.get_friend(friend_id)
        if not friend:
            return {
                "status": "error",
                "message": "Friend not found"
            }
        
        response = friend_api.read_messages(userStore.user_id, friend_id)

        if response.get("status") == "success":
            for message in friend.messages_list[::-1]:
                if message["is_read"] is False:
                    message["is_read"] = True
                else:
                    break
            friend.messages_list = [*friend.messages_list]
            FriendsStore().selected_friend = friend
            return {
                "status": "success",
                "message": "Friend selected successfully",
            }
        else:
            return {
                "status": "error",
                "message": response.get("message", "Failed to select friend")
            }

    def send_text_message(self, user_id: str, friend_id: str, text: str | None = '') -> dict:
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string")
        if not isinstance(friend_id, str):
            raise ValueError("Friend ID must be a string")
        if not isinstance(text, str | None):
            raise ValueError("Message must be a string")
        
        userStore = UserStore()
        if not userStore.is_authenticated:
            return {
                "status": "error",
                "message": "User is not authenticated"
            }
        
        friendStore = FriendsStore()
        friend = friendStore.get_friend(friend_id)
        if not friend:
            return {
                "status": "error",
                "message": "Friend not found"
            }
        
        dr_message = friend.doubleRatceht.encrypt(text)
        response = friend_api.create_text_message(user_id, friend_id, user_id, text, is_read=True)

        if response.get("status") == "success":
            data = response.get("data")

            message = {
                "sender_id": data['sender_id'],
                "text": data['text'],
                "timestamp": data['timestamp'],
                "is_read": data['is_read']
            }

            # Update FriendsStore
            friend.messages_list = [*friend.messages_list, message]

            # Propagation event
            socket = ClientSocket(friend.ip, friend.port)
            socket.send({
                "type": "text_message",
                "data": {
                    "sender_id": data["sender_id"],
                    "dr_message": dr_message,
                    "timestamp": data['timestamp'],
                }
            })

            return {
                "status": response.get("status", "success"),
                "message": response.get("message", "Message sent successfully"),
            }
        
        else:
            return {
                "status": response.get("status", "error"),
                "message": response.get("message", "Failed to send message")
            }

    def send_latent_message(self, user_id: str, friend_id: str, enc_latent_array: np.ndarray, enc_seed_bytes: str, seed_string: str) -> dict:
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string")
        if not isinstance(friend_id, str):
            raise ValueError("Friend ID must be a string")
        if not isinstance(enc_latent_array, np.ndarray):
            raise ValueError("Encoded latent tensor must be a np.ndarray")
        if not isinstance(enc_seed_bytes, bytes):
            raise ValueError("Encrypted seed string must be a string")
        if not isinstance(seed_string, str):
            raise ValueError("Seed string must be a string")
        
        userStore = UserStore()
        if not userStore.is_authenticated:
            return {
                "status": "error",
                "message": "User is not authenticated"
            }
        
        friendStore = FriendsStore()
        friend = friendStore.get_friend(friend_id)
        if not friend:
            return {
                "status": "error",
                "message": "Friend not found"
            }
        
        # Serialize
        buffer = io.BytesIO()
        np.save(buffer, enc_latent_array)
        enc_latent_bytes = buffer.getvalue()
        enc_latent_size = len(enc_latent_bytes)

        enc_seed_string = base64.b64encode(enc_seed_bytes).decode('utf-8')

        response = friend_api.create_latent_message(user_id, friend_id, user_id, enc_latent_size, enc_latent_array, enc_seed_string, seed_string, is_read=True)

        if response.get("status") == "success":
            data = response.get("data")

            # Skip deserialization and use previously encoded values

            message = {
                "sender_id": data['sender_id'],
                "enc_latent_array": enc_latent_array,
                "enc_latent_size": enc_latent_size,
                "enc_seed_bytes": enc_seed_bytes,
                "seed_string": data['seed_string'],
                "timestamp": data['timestamp'],
                "is_read": data['is_read']
            }

            # Update FriendsStore
            friend.messages_list = [*friend.messages_list, message]

            # Propagation event
            socket = ClientSocket(friend.ip, friend.port)
            socket.send({
                "type": "latent_message",
                "data": {
                    "sender_id": data["sender_id"],
                    "enc_latent_size": enc_latent_size,
                    "enc_seed_string": enc_seed_string,
                    "seed_string": None,
                    "timestamp": data['timestamp'],
                }
            }, binary_bytes=enc_latent_bytes, binary_type="pt")

            return {
                "status": response.get("status", "success"),
                "message": response.get("message", "Message sent successfully"),
            }
        
        else:
            return {
                "status": response.get("status", "error"),
                "message": response.get("message", "Failed to send message")
            }

    def unselect_friend(self) -> None:
        userStore = UserStore()
        if not userStore.is_authenticated:
            return {
                "status": "error",
                "message": "User is not authenticated"
            }
        
        FriendsStore().selected_friend = None
        return {
            "status": "success",
            "message": "Friend unselected successfully"
        }

    def update_friend_profile(self, user_id: str, friend_id: str, profile_image: Image.Image | None) -> dict:
        if not isinstance(friend_id, str):
            raise ValueError("Friend ID must be a string")
        if not isinstance(profile_image, Image.Image | None):
            raise ValueError("Profile image must be a PIL Image object")
        
        if not UserStore().is_authenticated:
            return {
                "status": "error",
                "message": "User is not authenticated"
            }
        
        # Serialize
        profile_base64 = image_to_base64(profile_image)

        response = friend_api.update_friend_profile(user_id, friend_id, profile_base64)

        if response.get("status") == "success":
            data = response.get("data")

            # Deserialize
            profile_image = base64_to_image(data["profile_base64"])

            # Update FriendsStore
            friend = FriendsStore().get_friend(friend_id)
            friend.profile_image = profile_image

            return {
                "status": response.get("status", "success"),
                "message": response.get("message", "Friend profile updated successfully"),
            }
        
        else:
            return {
                "status": response.get("status", "error"),
                "message": response.get("message", "Failed to update friend profile")
            }
    
    def _handle_socket_response(self, json_dict: dict, binary_bytes: bytes | None = None, binary_type: str | None = None):
        type = json_dict.get("type")
        data = json_dict.get("data")

        userStore = UserStore()

        print(f"[FriendController] Received socket response: {json_dict}"
              f"{' with binary data' if binary_bytes else ''}"
                f"{' of type ' + binary_type if binary_type else ''}")

        if type == "request_friend":
            # Accept friend request
            public_key = serialization.load_pem_public_key(data["public_key"].encode('utf-8'))
            profile_image = base64_to_image(data["profile_base64"])
            root_key =  ''.join(random.choices(string.ascii_letters + string.digits, k=16)).encode('utf-8')
            result = self.add_friend(
                user_id=userStore.user_id,
                ip=data["ip"],
                port=data["port"],
                friend_id=data["user_id"],
                public_key=public_key,
                profile_image=profile_image,
                root_key=root_key
            )
            if result["status"] == "success":
                # Send response
                root_key = encrypt_with_RSAKey(root_key, public_key).decode('utf-8')
                public_key = userStore.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode('utf-8')
                profile_base64 = image_to_base64(userStore.profile_image) if userStore.profile_image else None

                response_socket = ClientSocket(data["ip"], data["port"])
                response_socket.send({
                    "type": "response_friend",
                    "data": {
                        "ip": get_my_ip(),
                        "port": get_my_port(),
                        "user_id": userStore.user_id,
                        "public_key": public_key,
                        "profile_base64": profile_base64,
                        "root_key": root_key
                    }
                })

        elif type == "response_friend":
            # Accept friend request
            public_key = serialization.load_pem_public_key(data["public_key"].encode('utf-8'))
            profile_image = base64_to_image(data["profile_base64"])
            root_key = decrypt_with_RSAKey(base64.b64decode(data['root_key']), userStore.private_key)
            
            result = self.add_friend(
                user_id=userStore.user_id,
                ip=data["ip"],
                port=data["port"],
                friend_id=data["user_id"],
                public_key=public_key,
                profile_image=profile_image,
                root_key=root_key
            )
    
        elif type == "text_message":
            sender_id = data["sender_id"]
            dr_message = data["dr_message"]
            timestamp = data["timestamp"]
            self.receive_text_message(sender_id, dr_message, timestamp)

        elif type == "latent_message":
            sender_id = data["sender_id"]
            enc_latent_size = data["enc_latent_size"]
            enc_latent_array = np.load(io.BytesIO(binary_bytes)) if binary_bytes else None
            enc_seed_string = data["enc_seed_string"]
            seed_string = data.get("seed_string", None)
            timestamp = data["timestamp"]
            self.receive_latent_message(sender_id, enc_latent_size, enc_latent_array, enc_seed_string, seed_string, timestamp)