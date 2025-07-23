from api import user_api
from utils.image import base64_to_image
from states.observable import Observable
from PIL import Image
from utils.socket.client_socket import ClientSocket

class Friend(Observable):
    def __init__(self, ip: str, user_id: str, friend_id: str, public_key: str, profile_image: Image.Image | None):
        super().__init__()
        self.ip = ip
        self.user_id = user_id
        self.friend_id = friend_id
        self.public_key = public_key
        self._profile_image = profile_image

    @property
    def profile_image(self):
        return self._profile_image
    
    @profile_image.setter
    def profile_image(self, value: Image.Image | None):
        self._profile_image = value
        self.notify_observers("profile_image")


class FriendsStore(Observable):
    _instance = None
    _initialized = False # 

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not FriendsStore._initialized:
            super().__init__() 
            self._init_state()
            FriendsStore._initialized = True #

    def _init_state(self):
        self._friends_list = []

    @property
    def friends_list(self):
        return self._friends_list

    @friends_list.setter
    def friends_list(self, value):
        if self._friends_list != value:
            self._friends_list = value
            self.notify_observers("friends_list")

    def get_friend(self, friend_id: str):
        for friend in self.friends_list:
            if friend.friend_id == friend_id:
                return friend
        return None

    def add_friend(self, friend: Friend):
        self.friends_list = [*self.friends_list, friend]

    def remove_friend(self, friend_id: str):
        self.friends_list = [friend for friend in self.friends_list if friend.friend_id != friend_id]

    def reset(self):
        self._init_state()