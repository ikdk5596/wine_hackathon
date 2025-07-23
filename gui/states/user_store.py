from api import user_api
from utils.image import base64_to_image
from states.observable import Observable
from states.friends_store import FriendsStore

class UserStore(Observable):
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not UserStore._initialized:
            super().__init__()
            self._init_state()
            UserStore._initialized = True 

    def _init_state(self):
        self._user_id = None
        self.password = None
        self.private_key = None
        self.public_key = None
        self._profile_image = None

    @property
    def user_id(self):
        return self._user_id
    
    @property
    def profile_image(self):
        return self._profile_image

    @property
    def is_authenticated(self):
        return self._user_id
    
    @user_id.setter
    def user_id(self, value):
        if self._user_id != value:
            self._user_id = value
            self.notify_observers("user_id")

    @profile_image.setter
    def profile_image(self, value):   
        if self._profile_image != value:
            self._profile_image = value
            self.notify_observers("profile_image")

    def reset(self):
        self._init_state()