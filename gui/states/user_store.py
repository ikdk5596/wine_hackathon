from api import users
from utils.image import base64_to_image
from states.observable import Observable

class UserStore(Observable):
    _instance = None
    _initialized = False # <--- 이 플래그를 추가하세요!

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not UserStore._initialized:
            super().__init__() # <--- Observable의 __init__을 여기서 딱 한 번 호출
            self._init_state() # UserStore의 고유 초기화
            UserStore._initialized = True # <--- 초기화 완료!

    def _init_state(self):
        self._user_id = None
        self._password = None
        self._private_key = None
        self._public_key = None
        self._profile = None
        self._is_authenticated = False

    @property
    def user_id(self):
        return self._user_id
    
    @property
    def profile(self):
        return self._profile

    @property
    def is_authenticated(self):
        return self._is_authenticated
    
    @user_id.setter
    def user_id(self, value):
        if self._user_id != value:
            self._user_id = value
            self.notify_observers("user_id")

    @profile.setter
    def profile(self, value):   
        if self._profile != value:
            self._profile = value
            self.notify_observers("profile")

    def sign_up(self, user_id, password) -> bool:
        return users.register_user(user_id, password)

    def login(self, user_id, password):
        result = users.authenticate_user(user_id, password)
        if not result:
            raise False
        else:
            self._user_id = user_id
            self.password = password
            self.private_key = result.get("private_key", None)
            self.public_key = result.get("public_key", None)
            self._profile = result.get("profile", None)
            if self._profile:
                self._profile = base64_to_image(self._profile)
            self._is_authenticated = True
            return True
        
    def update_picture(self, picture: str):
        if not self.is_authenticated:
            raise Exception("User is not authenticated")
        
        if users.update_profile(self._user_id, picture):
            self.profile = base64_to_image(picture) if picture else None

    def logout(self):
        self._init_state()
