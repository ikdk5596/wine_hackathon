import customtkinter as ctk
from ui.atoms.banner import Banner
from ui.organisms.my_profile import MyProfile
from ui.organisms.friends_list import FriendsList

class MainPage(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.configure(fg_color="white", corner_radius=0)

        self.header = Banner(self)
        self.header.pack(fill="x")

        self.my_profile = MyProfile(self, controller)
        self.my_profile.pack(fill="x")

        top_border_frame = ctk.CTkFrame(self, height=2, fg_color="#e4e4e4")
        top_border_frame.pack(fill="x", padx=0, pady=(10, 2))

        self.friends_list = FriendsList(self, controller)
        self.friends_list.pack(fill="both", expand=True)
