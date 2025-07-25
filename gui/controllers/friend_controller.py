import io
import base64
import random
import string
import torch
import numpy as np
from PIL import Image
from api import friend_api
from utils.network import get_my_ip, get_my_port
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from utils.core.encoding import encode_image_to_latent
from utils.core.encryption import encrypt_latent, encrypt_with_RSAKey
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

    def add_friend(self, user_id: str, ip: str, port: int, friend_id: str, public_key: RSAPublicKey, profile_image: Image.Image | None) -> dict:
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
        
        if not UserStore().is_authenticated:
            return {
                "status": "error",
                "message": "User is not authenticated"
            }
        
        # Serialize
        public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        profile_base64 = image_to_base64(profile_image) if profile_image else None

        response = friend_api.create_friend(user_id, ip, port, friend_id, public_key, profile_base64)

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
                messages_list=[]
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

        if response.get("status") == "success":
            data = response.get("data")
            
            # Deserialize friends
            friends_list = []
            for friend in data["friends"]:
                friend["public_key"] = serialization.load_pem_public_key(friend["public_key"].encode('utf-8'))
                friend["profile_image"] = base64_to_image(friend["profile_base64"])
                messages_list = []
                for message in friend["messages_list"]:
                    enc_latent_tensor = None
                    enc_seed_bytes = None
                    if message.get("enc_latent_string"):
                        buffer = io.BytesIO(base64.b64decode(message["enc_latent_string"]))
                        npz_file = np.load(buffer)
                        enc_latent_tensor = torch.tensor(npz_file['latent'])              
                    if message.get("enc_seed_string"):      
                        enc_seed_bytes = base64.b64decode(message["enc_seed_string"])
                    messages_list.append({
                        "sender_id": message['sender_id'],
                        "text": message['text'],
                        "enc_latent_tensor": enc_latent_tensor,
                        "enc_seed_bytes": enc_seed_bytes,
                        "seed_string": message['seed_string'],
                        "timestamp": message['timestamp'],
                        "is_read": message['is_read']
                    })
                friends_list.append(Friend(
                    user_id=friend["user_id"],
                    ip=friend["ip"],
                    port=friend["port"],
                    friend_id=friend["friend_id"],
                    public_key=friend["public_key"],
                    profile_image=friend["profile_image"],
                    messages_list= messages_list
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
    
    def receive_message(self, friend_id: str, text: str, enc_latent_string: str | None, enc_seed_string: str | None, timestamp: float) -> None:
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
        response = friend_api.create_message(userStore.user_id, friend_id, friend_id, text,
                                             enc_latent_string, enc_seed_string, seed_string=None,
                                             timestamp=timestamp, is_read=is_read)

        if response.get("status") == "success":
            data = response.get("data")

            # Deserialize
            enc_latent_tensor = None
            enc_seed_bytes = None
            if data.get("enc_latent_string"):
                buffer = io.BytesIO(base64.b64decode(data["enc_latent_string"]))
                npz_file = np.load(buffer)
                enc_latent_tensor = torch.tensor(npz_file['latent'])
            if data.get("enc_seed_string"):
                buffer = io.BytesIO(base64.b64decode(data["enc_seed_string"]))
                enc_seed_bytes = buffer.read()

            # Update FriendsStore
            message = {
                "sender_id": data['sender_id'],
                "text": data['text'],
                "timestamp": data['timestamp'],
                "enc_latent_tensor": enc_latent_tensor,
                "enc_seed_bytes": enc_seed_bytes,
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

    
    def send_message(self, user_id: str, friend_id: str, text: str | None = '', image: Image.Image | None = None) -> dict:
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string")
        if not isinstance(friend_id, str):
            raise ValueError("Friend ID must be a string")
        if not isinstance(text, str | None):
            raise ValueError("Message must be a string")
        if not isinstance(image, Image.Image | None):
            raise ValueError("Image must be a PIL Image object or None")
        
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
        
        enc_latent_tensor = None
        enc_latent_string = None
        enc_seed_bytes = None
        enc_seed_string = None
        seed_string = None

        if image:
            # encode
            latent_tensor = encode_image_to_latent(image)
            
            # encrypt latent
            seed_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            enc_latent_tensor = encrypt_latent(latent_tensor, seed_string)
            buffer = io.BytesIO()
            arr = enc_latent_tensor.detach().cpu().numpy()
            np.savez_compressed(buffer, latent=arr)
            enc_latent_bytes = buffer.getvalue()
            enc_latent_string = base64.b64encode(enc_latent_bytes).decode("utf-8")
            
            # encrypt_seed
            enc_seed_bytes = encrypt_with_RSAKey(seed_string.encode('utf-8'), friend.public_key)
            enc_seed_string = base64.b64encode(enc_seed_bytes).decode('utf-8')

        response = friend_api.create_message(user_id, friend_id, user_id, text, enc_latent_string, enc_seed_string, seed_string, is_read=True)

        if response.get("status") == "success":
            data = response.get("data")

            message = {
                "sender_id": data['sender_id'],
                "text": data['text'],
                "enc_latent_tensor": enc_latent_tensor,
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
                "type": "new_message",
                "data": {
                    "sender_id": data["sender_id"],
                    "text": data['text'],
                    "enc_latent_tensor": data["enc_latent_string"],
                    "enc_seed_string": data['enc_seed_string'],
                    "seed_string": None,
                    "timestamp": data['timestamp'],
                    "is_read": data['is_read']
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
    
    def _handle_socket_response(self, response):
        type = response.get("type")
        data = response.get("data")

        userStore = UserStore()

        if type == "request_friend":
            # Accept friend request
            public_key = serialization.load_pem_public_key(data["public_key"].encode('utf-8'))
            profile_image = base64_to_image(data["profile_base64"])
            self.add_friend(
                user_id=userStore.user_id,
                ip=data["ip"],
                port=data["port"],
                friend_id=data["user_id"],
                public_key=public_key,
                profile_image=profile_image
            )
            # Send response
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
                    "profile_base64": profile_base64
                }
            })

        elif type == "response_friend":
            # Accept friend request
            public_key = serialization.load_pem_public_key(data["public_key"].encode('utf-8'))
            profile_image = base64_to_image(data["profile_base64"])
            self.add_friend(
                user_id=userStore.user_id,
                ip=data["ip"],
                port=data["port"],
                friend_id=data["user_id"],
                public_key=public_key,
                profile_image=profile_image
            )
    
        elif type == "new_message":
            sender_id = data["sender_id"]
            text = data["text"]
            enc_latent_string = data.get("enc_latent_tensor", None)
            enc_seed_string = data.get("enc_seed_string", None)
            timestamp = data["timestamp"]
            self.receive_message(sender_id, text, enc_latent_string, enc_seed_string, timestamp)