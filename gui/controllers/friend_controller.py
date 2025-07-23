from api import friend_api
from utils.image import base64_to_image, image_to_base64
from states.user_store import UserStore
from states.friends_store import FriendsStore, Friend
from utils.socket.server_socket import ServerSocket
from utils.socket.client_socket import ClientSocket
from PIL import Image
from utils.ip import get_my_ip
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from utils.core.encoding import encode_image_to_latent, decode_latent_to_image
from utils.core.encryption import decrypt_latent, encrypt_latent
import random
import string
import numpy as np
import io
import torch
from cryptography.hazmat.primitives.asymmetric import padding

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
        print("[FriendController] Initialized")  # 처음 1번만 호출됨
        ServerSocket().add_callback(self._handle_socket_response)

    def load_friends(self, user_id: str = None) -> dict:
        response = friend_api.get_friends(user_id or UserStore().user_id)
        if response.get("status") == "success":
            friends_data = response.get("friends", [])
            friends_list = []
            for friend_data in friends_data:
                profile_image = base64_to_image(friend_data.get("profile_base64")) if friend_data.get("profile_base64") else None
                messages_list = friend_data.get("messages_list", [])
                for message in messages_list:
                    if message.get("latent_tensor"):
                        buffer = io.BytesIO(message["latent_tensor"])
                        npz_file = np.load(buffer)
                        message["latent_tensor"] = torch.tensor(npz_file['latent'])
                    else:
                        message["latent_tensor"] = None
                friend = Friend(
                    ip=friend_data.get("ip"),
                    user_id=friend_data.get("user_id"),
                    friend_id=friend_data.get("friend_id"),
                    public_key=friend_data.get("public_key"),
                    profile_image=profile_image,
                    messages_list=friend_data.get("messages_list", [])
                )
                friends_list.append(friend)
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

    def request_friend(self, ip: str) -> dict:
        if not isinstance(ip, str):
            raise ValueError("IP address must be a string")
        
        request_socket = ClientSocket(ip)
        request_socket.send({
            "type": "request_friend",
            "data": {
                "ip": get_my_ip(),
                "friend_id": UserStore().user_id,
                "public_key": UserStore().public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode('utf-8'),  
                "profile_base64": image_to_base64(UserStore().profile_image) if UserStore().profile_image else None
                }
            })

        return {
            "status": "success",
            "message": "Friend request sent successfully"
        }
    
    def add_friend(self, user_id: str, ip: str, friend_id: str, public_key: RSAPublicKey, profile_image: Image.Image | None) -> dict:
        if not isinstance(ip, str):
            raise ValueError("IP address must be a string")
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string")
        if not isinstance(friend_id, str):
            raise ValueError("Friend ID must be a string")
        if not isinstance(public_key, RSAPublicKey):
            raise ValueError("Public key must be a RSAPublicKey object")
        if not isinstance(profile_image, Image.Image | None):
            raise ValueError("Profile image must be a PIL Image object")
        
        profile_base64 = image_to_base64(profile_image) if profile_image else None
        response = friend_api.create_friend(user_id, ip, friend_id, public_key, profile_base64)

        if response.get("status") == "success":
            friend = Friend(
                ip=ip,
                user_id=user_id,
                friend_id=friend_id,
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

    def update_friend_profile(self, friend_id: str, profile_image: Image.Image | None) -> dict:
        if not isinstance(friend_id, str):
            raise ValueError("Friend ID must be a string")
        if not isinstance(profile_image, Image.Image | None):
            raise ValueError("Profile image must be a PIL Image object")
        
        profile_base64 = image_to_base64(profile_image)
        response = friend_api.update_friend_profile(friend_id, profile_base64)

        if response.get("status") == "success":
            friend = FriendsStore().get_friend(friend_id)
            friend.profile_image = base64_to_image(response.get("profile_base64"))
            return {
                "status": response.get("status", "success"),
                "message": response.get("message", "Friend profile updated successfully"),
            }
        else:
            return {
                "status": response.get("status", "error"),
                "message": response.get("message", "Failed to update friend profile")
            }
        
    def delete_friend(self, user_id: str, friend_id: str) -> dict:
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string")
        if not isinstance(friend_id, str):
            raise ValueError("Friend ID must be a string")
        
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
        
    def select_friend(self, friend_id: str) -> None:
        if not isinstance(friend_id, str):
            raise ValueError("Friend ID must be a string")
        
        friend = FriendsStore().get_friend(friend_id)
        if friend:
            FriendsStore().selected_friend = friend
        else:
            raise ValueError(f"Friend with ID {friend_id} not found")
    
    def send_message(self, user_id: str, friend_id: str, text: str = '', image: Image.Image | None = None) -> dict:
        print("???")
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string")
        if not isinstance(friend_id, str):
            raise ValueError("Friend ID must be a string")
        if not isinstance(text, str):
            raise ValueError("Message must be a string")
        if not isinstance(image, Image.Image | None):
            raise ValueError("Image must be a PIL Image object or None")
        
        latent_bytes = None
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
            encrypted_seed = friend.public_key.encrypt(
                seed.encode('utf-8'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # latent_bytes
            buffer = io.BytesIO()
            arr = encrypted_tensor.detach().cpu().numpy()
            np.savez_compressed(buffer, latent=arr)
            latent_bytes = buffer.getvalue()

        response = friend_api.create_message(user_id, friend_id, user_id, text, latent_bytes, encrypted_seed, is_read=True)

        if response.get("status") == "success":
            friend = FriendsStore().get_friend(friend_id)
            print("friend:", friend)
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
                print(friend.messages_list)
            socket = ClientSocket(friend.ip)
            socket.send({
                "type": "new_message",
                "data": {
                    "sender_id": user_id,
                    "text": response['text'],
                    "timestamp": response['timestamp'],
                    "latent_bytes": response.get('latent_bytes', None),
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
    
    def receive_message(self, friend_id: str, text: str, latent_bytes: bytes | None, encrypted_seed: str | None, timestamp: float) -> None:
        response = friend_api.create_message(UserStore().user_id, friend_id, friend_id, text, latent_bytes, encrypted_seed, timestamp)

        if response.get("status") == "success":
            friend = FriendsStore().get_friend(friend_id)
            if friend:
                if latent_bytes:
                    buffer = io.BytesIO(latent_bytes)
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
    
    def _handle_socket_response(self, response):
        print(f"[FriendController] Received socket response: {response}")
        if response.get("type") == "request_friend":
            self.add_friend(
                user_id=UserStore().user_id,
                ip=response.get("data").get("ip"),
                friend_id=response.get("data").get("friend_id"),
                public_key=serialization.load_pem_public_key(response.get("data").get("public_key").encode('utf-8')),
                profile_image=base64_to_image(response.get("data").get("profile_base64")) if response.get("data").get("profile_base64") else None
            )
            response_socket = ClientSocket(response.get("data").get("ip"))
            response_socket.send({
                "type": "response_friend",
                "data": {
                    "ip": get_my_ip(),
                    "friend_id": UserStore().user_id,
                    "public_key": UserStore().public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ).decode('utf-8'),  
                    "profile_base64": image_to_base64(UserStore().profile_image) if UserStore().profile_image else None
                }
            })
        elif response.get("type") == "response_friend":
            self.add_friend(
                user_id=UserStore().user_id,
                ip=response.get("data").get("ip"),
                friend_id=response.get("data").get("friend_id"),
                public_key=serialization.load_pem_public_key(response.get("data").get("public_key").encode('utf-8')),
                profile_image=base64_to_image(response.get("data").get("profile_base64")) if response.get("data").get("profile_base64") else None
            )
        elif response.get("type") == "new_message":
            sender_id = response.get("data").get("sender_id")
            text = response.get("data").get("text")
            latent_bytes = response.get("data").get("latent_bytes")
            encrypted_seed = response.get("data").get("encrypted_seed")
            timestamp = response.get("data").get("timestamp")
            self.receive_message(sender_id, text, latent_bytes, encrypted_seed, timestamp)