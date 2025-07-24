import customtkinter as ctk
from ui.atoms.toast import Toast
from ui.atoms.button import Button
from ui.atoms.input import Input
from controllers.friend_controller import FriendController

class AddFriend(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="white", corner_radius=0)
        self.controller = controller
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.ip_entry = Input(self, placeholder="Friend IP", width=200)
        self.ip_entry.pack(padx=50, pady=(20, 10))

        self.port_entry = Input(self, placeholder="Friend Port", width=200)
        self.port_entry.pack(pady=(0, 10))

        self.button = Button(self, text="Request", command=self.add_friend)
        self.button.pack(pady=(10, 20))

    def add_friend(self):
        ip = self.entry.get()
        port = int(self.port_entry.get())

        try:
            result = FriendController().request_friend(ip, port)
            if result['status'] == 'success':
                Toast(self.controller, result['message'], type="success", duration=2000)
            else:
                Toast(self.controller, result['message'], type="error", duration=2000)
        except Exception as e:
            Toast(self, f"Error: {str(e)}", type="error", duration=2000)