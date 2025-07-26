import customtkinter as ctk
from ui.atoms.banner import Banner
from ui.atoms.button import Button
from ui.organisms.messages_list import MessagesList
from ui.organisms.chat_input import ChatInput
from controllers.friend_controller import FriendController

class ChatPage(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.configure(fg_color="#e6e9ed", corner_radius=0)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.header = Banner(self)
        self.header.grid(row=0, column=0, sticky="nsew")

        back_button = Button(self, type="white", text="<", width=12, height=12, command=self.go_back)
        back_button.grid(row=1, column=0, sticky="nw", padx=5, pady=5)

        self.messages_list = MessagesList(self)
        self.messages_list.grid(row=2, column=0, sticky="nsew")

        self.chat_input = ChatInput(self)
        self.chat_input.grid(row=3, column=0, sticky="nsew")

    def go_back(self):
        self.controller.show_frame("MainPage")
        FriendController().unselect_friend()