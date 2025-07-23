from states.observable import Observable
from PIL import Image

class Friend(Observable):
    def __init__(self, ip: str, user_id: str, friend_id: str, public_key: str, profile_image: Image.Image | None, messages_list: list):
        super().__init__()
        self.ip = ip
        self.user_id = user_id
        self.friend_id = friend_id
        self.public_key = public_key
        self._profile_image = profile_image
        self._messages_list = messages_list

    @property
    def profile_image(self):
        return self._profile_image
    
    @property
    def messages_list(self):
        return self._messages_list
    
    @profile_image.setter
    def profile_image(self, value: Image.Image | None):
        self._profile_image = value
        self.notify_observers("profile_image")

    @messages_list.setter
    def messages_list(self, value: list):
        self._messages_list = value
        self.notify_observers("messages_list")


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
            FriendsStore._initialized = True

    def _init_state(self):
        self._friends_list = []
        self._selected_friend = None

    @property
    def friends_list(self):
        return self._friends_list
    
    @property
    def selected_friend(self):
        return self._selected_friend

    @friends_list.setter
    def friends_list(self, value):
        if self._friends_list != value:
            self._friends_list = value
            self.notify_observers("friends_list")

    @selected_friend.setter
    def selected_friend(self, value):
        if self._selected_friend != value:
            self._selected_friend = value
            self.notify_observers("selected_friend")

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