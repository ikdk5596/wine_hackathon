from urllib import response
from api import user_api
from utils.image import base64_to_image, image_to_base64
from states.user_store import UserStore
from states.friends_store import FriendsStore
from utils.socket.server_socket import ServerSocket
from utils.socket.client_socket import ClientSocket
from PIL import Image
from controllers.friend_controller import FriendController

class UserController:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        if not UserController._initialized:
            super().__init__()
            self._init_state()
            UserController._initialized = True 

    def _init_state(self):
        print("[UserController] Initialized")  # 처음 1번만 호출됨
        ServerSocket().add_callback(self._handle_socket_response)

    def login(self, user_id: str, password:str) -> dict:
        if not isinstance(user_id, str):
            raise ValueError("User ID and password must be strings")
        if not isinstance(password, str):
            raise ValueError("User ID and password must be strings")
        
        response = user_api.authenticate_user(user_id, password)

        if response.get("status") == "success":
            UserStore().user_id = response.get("user_id")
            UserStore().private_key = response.get("private_key")
            UserStore().public_key = response.get("public_key")
            UserStore().profile_image = base64_to_image(response.get("profile_base64"))
            FriendController().load_friends()
            return {
                "status": response.get("status", "success"),
                "message": response.get("message", "Login successful"),
            }
        else:
            return {
                "status": response.get("status", "error"),
                "message": response.get("message", "Login failed")
            }
        
    def logout(self):
        UserStore().reset()
        FriendsStore().reset()
        return {
            "status": "success",
            "message": "User logged out successfully"
        }
        
    def sign_up(self, user_id: str, password: str) -> dict:
        print(1)
        if not isinstance(user_id, str):
            raise ValueError("User ID and password must be strings")
        if not isinstance(password, str):
            raise ValueError("User ID and password must be strings")
        
        response = user_api.create_user(user_id, password)
        print(response)


        if response.get("status") == "success":
            return {
                "status": response.get("status", "success"),
                "message": response.get("message", "Sign up successful"),
            }
        else:
            return {
                "status": response.get("status", "error"),
                "message": response.get("message", "Sign up failed")
            }

    def update_profile_image(self, user_id: str, profile_image: Image.Image | None) -> bool:
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string")
        if not isinstance(profile_image, Image.Image | None):
            raise ValueError("Profile image must be a PIL Image object")
        
        if not UserStore().is_authenticated:
            return {
                "status": "error",
                "message": "User is not authenticated"
            }
        
        profile_base64 = image_to_base64(profile_image)
        response = user_api.update_user_profile(user_id, profile_base64)
        print(response)
        if response.get("status") == "success":
            UserStore().profile_image = base64_to_image(response.get("profile_base64"))
            for friend in FriendsStore().friends_list:
                friend_socket = ClientSocket(friend.ip)
                print(f"Sending profile update to {friend.ip}")
                friend_socket.send({
                    "type": "profile_update",
                    "data": {
                        "user_id": response.get("user_id"),
                        "profile_base64": response.get("profile_base64"),
                        }
                    })
            return {
                "status": response.get("status", "success"),
                "message": response.get("message", "Profile updated successfully"),
                "profile_base64": response.get("profile_base64")
            }
        else:
            return {
                "status": response.get("status", "error"),
                "message": response.get("message", "Profile update failed")
            }
        
    def _handle_socket_response(self, response):
        if response.get("type") == "profile_update":
            FriendController().update_friend_profile(
                response.get("data").get("user_id"),
                base64_to_image(response.get("data").get("profile_base64"))
            )