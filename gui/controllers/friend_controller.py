from api import friend_api
from utils.image import base64_to_image, image_to_base64
from states.user_store import UserStore
from states.friends_store import FriendsStore, Friend
from utils.socket.server_socket import ServerSocket
from utils.socket.client_socket import ClientSocket
from PIL import Image
from utils.ip import get_my_ip
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

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
    
    def send_message(self, user_id: str, friend_id: str, text: str) -> dict:
        print("???")
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string")
        if not isinstance(friend_id, str):
            raise ValueError("Friend ID must be a string")
        if not isinstance(text, str):
            raise ValueError("Message must be a string")
        
        print(f"[FriendController] Sending message from {user_id} to {friend_id}: {text}")
        
        response = friend_api.create_message(user_id, friend_id, user_id, text, is_read=True)

        if response.get("status") == "success":
            friend = FriendsStore().get_friend(friend_id)
            print("friend:", friend)
            if friend:
                message = {
                    "sender_id": user_id,
                    "text": response['text'],
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
    
    def receive_message(self, friend_id: str, text: str, timestamp: float) -> None:
        response = friend_api.create_message(UserStore().user_id, friend_id, friend_id, text, timestamp)

        if response.get("status") == "success":
            friend = FriendsStore().get_friend(friend_id)
            if friend:
                message = {
                    "sender_id": friend_id,
                    "text": response['text'],
                    "timestamp": response['timestamp'],
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
        if response.get("type") == "response_friend":
            self.add_friend(
                user_id=UserStore().user_id,
                ip=response.get("data").get("ip"),
                friend_id=response.get("data").get("friend_id"),
                public_key=serialization.load_pem_public_key(response.get("data").get("public_key").encode('utf-8')),
                profile_image=base64_to_image(response.get("data").get("profile_base64")) if response.get("data").get("profile_base64") else None
            )
        elif response.get("type") == "new_message":
            friend_id = response.get("data").get("friend_id")
            text = response.get("data").get("text")
            timestamp = response.get("data").get("timestamp")
            self.receive_message(friend_id, text, timestamp)