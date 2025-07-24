import customtkinter as ctk
from ui.atoms.toast import Toast
from ui.atoms.button import Button
from ui.atoms.input import Input
from controllers.friend_controller import FriendController

class AddFriend(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="white", corner_radius=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.entry = Input(self, placeholder="Friend IP")
        self.entry.pack(pady=(20, 10))

        self.button = Button(self, text="Request", command=self.add_friend)
        self.button.pack()

    def add_friend(self):
        ip = self.entry.get()

        # try:
        result = FriendController().request_friend(ip)
        if result['status'] == 'success':
            Toast(self, result['message'], type="success", duration=2000)
        else:
            Toast(self, result['message'], type="error", duration=2000)
        # except Exception as e:
        #     Toast(self, f"Error: {str(e)}", type="error", duration=2000)