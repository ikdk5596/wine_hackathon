from PIL import Image
from cryptography.hazmat.primitives import serialization
from api import user_api
from utils.image import base64_to_image, image_to_base64
from states.user_store import UserStore
from states.friends_store import FriendsStore
from utils.socket.server_socket import ServerSocket
from utils.socket.client_socket import ClientSocket
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
        ServerSocket().add_callback(self._handle_socket_response)

    def login(self, user_id: str, password:str) -> dict:
        if not isinstance(user_id, str) or user_id == "":
            raise ValueError("User ID and password must be strings")
        if not isinstance(password, str) or password == "":
            raise ValueError("User ID and password must be strings")
        
        response = user_api.authenticate_user(user_id, password)

        if response.get("status") == "success":
            data = response.get("data")
            
            # Deserialize data
            private_key = serialization.load_pem_private_key(
                data["private_key"].encode('utf-8'),
                password=None
            )
            public_key = serialization.load_pem_public_key(
                data["public_key"].encode('utf-8')
            )
            profile_image = base64_to_image(data.get("profile_base64"))

            # Update UserStore
            userStore = UserStore()
            userStore.user_id = data["user_id"]
            userStore.private_key = private_key
            userStore.public_key = public_key
            userStore.profile_image = profile_image

            # Propagation event
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
        if not isinstance(user_id, str) or user_id == "":
            raise ValueError("User ID and password must be strings")
        if not isinstance(password, str) or password == "":
            raise ValueError("User ID and password must be strings")
        
        response = user_api.create_user(user_id, password)

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
        
        userStore = UserStore()

        if not userStore.is_authenticated:
            return {
                "status": "error",
                "message": "User is not authenticated"
            }
        
        profile_base64 = image_to_base64(profile_image)
        response = user_api.update_user_profile(user_id, profile_base64)
        
        if response.get("status") == "success":
            data = response.get("data")

            # Update UserStore
            userStore.profile_image = base64_to_image(data["profile_base64"])
            
            # Propagation event
            for friend in FriendsStore().friends_list:
                friend_socket = ClientSocket(friend.ip, friend.port)
                friend_socket.send({
                    "type": "profile_update",
                    "data": {
                        "user_id": data["user_id"],
                        "profile_base64": data["profile_base64"],
                        }
                    })
                
            return {
                "status": response.get("status", "success"),
                "message": response.get("message", "Profile updated successfully"),
            }
        else:
            return {
                "status": response.get("status", "error"),
                "message": response.get("message", "Profile update failed")
            }
        
    def _handle_socket_response(self, response):
        userStore = UserStore()

        type = response.get("type")
        data = response.get("data")

        if type == "profile_update":
            user_id =  userStore.user_id
            friend_id = data.get("user_id")
            profile_image = base64_to_image(data.get("profile_base64"))
            FriendController().update_friend_profile(
                user_id,
                friend_id,
                profile_image
            )