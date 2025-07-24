from api import friend_api
from utils.image import base64_to_image, image_to_base64
from states.user_store import UserStore
from states.friends_store import FriendsStore, Friend
from utils.socket.server_socket import ServerSocket
from utils.socket.client_socket import ClientSocket
from PIL import Image
from utils.network import get_my_ip, get_my_port
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from utils.core.encoding import encode_image_to_latent
from utils.core.encryption import decrypt_latent, encrypt_latent
import random
import string
import numpy as np
import io
import torch
from cryptography.hazmat.primitives.asymmetric import padding
import base64

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
                for message in friend["messages_list"]:
                    if message.get("latent_string"):
                        buffer = io.BytesIO(base64.b64decode(message["latent_string"]))
                        npz_file = np.load(buffer)
                        message["latent_tensor"] = torch.tensor(npz_file['latent'])
                    else:
                        message["latent_tensor"] = None
                friends_list.append(Friend(*friend))
            
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
    
    def receive_message(self, friend_id: str, text: str, latent_string: str | None, encrypted_seed: str | None, timestamp: float) -> None:
        response = friend_api.create_message(UserStore().user_id, friend_id, friend_id, text, latent_string, encrypted_seed, timestamp)

        if response.get("status") == "success":
            friend = FriendsStore().get_friend(friend_id)
            if friend:
                latent_tensor = None
                if latent_string:
                    buffer = io.BytesIO(base64.b64decode(latent_string))
                    npz_file = np.load(buffer)
                    latent_tensor = torch.tensor(npz_file['latent'])

                message = {
                    "sender_id": friend_id,
                    "text": response['text'],
                    "timestamp": response['timestamp'],
                    "latent_tensor": latent_tensor,
                    "encrypted_seed": response.get('encrypted_seed', None),
                    "is_read": response['is_read']
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
        
        friend = FriendsStore().get_friend(friend_id)

        if friend:
            FriendsStore().selected_friend = friend
            return {
                "status": "success",
                "message": "Friend selected successfully",
            }
        else:
            return {
                "status": "error",
                "message": "Friend not found"
            }
    
    def send_message(self, user_id: str, friend_id: str, text: str = '', image: Image.Image | None = None) -> dict:
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string")
        if not isinstance(friend_id, str):
            raise ValueError("Friend ID must be a string")
        if not isinstance(text, str):
            raise ValueError("Message must be a string")
        if not isinstance(image, Image.Image | None):
            raise ValueError("Image must be a PIL Image object or None")
        
        latent_bytes = None
        latent_string = None
        encrypted_seed = None
        encrypted_tensor = None

        if image:
            # encode
            latent_tensor = encode_image_to_latent(image)
            
            # encrypt
            seed = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            encrypted_tensor = encrypt_latent(latent_tensor, seed)
            
            # encrypt_seed
            friend = FriendsStore().get_friend(friend_id)
            encrypted_seed_bytes = friend.public_key.encrypt(
                seed.encode('utf-8'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            encrypted_seed = base64.b64encode(encrypted_seed_bytes).decode('utf-8')

            # latent_bytes
            buffer = io.BytesIO()
            arr = encrypted_tensor.detach().cpu().numpy()
            np.savez_compressed(buffer, latent=arr)
            latent_bytes = buffer.getvalue()
            latent_string = base64.b64encode(latent_bytes).decode("utf-8")

        response = friend_api.create_message(user_id, friend_id, user_id, text, latent_string, encrypted_seed, is_read=True)

        if response.get("status") == "success":
            friend = FriendsStore().get_friend(friend_id)
            if friend:
                message = {
                    "sender_id": user_id,
                    "text": response['text'],
                    "latent_tensor": encrypted_tensor,
                    "encrypted_seed": response.get('encrypted_seed', None),
                    "timestamp": response['timestamp'],
                    "is_read": response['is_read']
                }
                friend.messages_list = [*friend.messages_list, message]
            socket = ClientSocket(friend.ip)
            socket.send({
                "type": "new_message",
                "data": {
                    "sender_id": user_id,
                    "text": response['text'],
                    "timestamp": response['timestamp'],
                    "latent_string": latent_string,
                    "encrypted_seed": response.get('encrypted_seed', None),
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
            sender_id = response.get("data").get("sender_id")
            text = response.get("data").get("text")
            latent_string = response.get("data").get("latent_string")
            encrypted_seed = response.get("data").get("encrypted_seed")
            timestamp = response.get("data").get("timestamp")
            self.receive_message(sender_id, text, latent_string, encrypted_seed, timestamp)