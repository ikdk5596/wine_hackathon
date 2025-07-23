import customtkinter as ctk
import tkinter.filedialog as fd
from ui.atoms.button import Button
from states.friends_store import FriendsStore
from states.user_store import UserStore
from controllers.friend_controller import FriendController

class ChatInput(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.configure(fg_color="white", corner_radius=0)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Label
        label = ctk.CTkLabel(self, text="Chat Message", text_color="#7A7A8B")
        label.grid(row=0, column=0, sticky="w", padx=10, pady=(5, 2), columnspan=2)

        # Textbox with internal scroll
        self.textbox = ctk.CTkTextbox(self, height=80, wrap="word") 
        self.textbox.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10))

        # File picker button
        self.file_button = Button(self, type="white", text="Choose file", command=self.pick_file, width=100)
        self.file_button.grid(row=2, column=0, sticky="w", padx=10, pady=10)

        # Send button
        self.send_button = Button(self, text="Send", command=self.send_message, width=100)
        self.send_button.grid(row=2, column=1, sticky="e", padx=10, pady=10)

        self.selected_file = None

    def pick_file(self):
        path = fd.askopenfilename()
        if path:
            self.selected_file = path
            self.file_button.configure(text="File chosen")
        else:
            self.selected_file = None
            self.file_button.configure(text="Choose file")

    def send_message(self):
        message = self.textbox.get("0.0", "end").strip()
        FriendController().send_message(
            UserStore().user_id,
            FriendsStore().selected_friend.friend_id,
            message
        )
        self.textbox.delete("0.0", "end")
        self.selected_file = None
        self.file_button.configure(text="Choose file")