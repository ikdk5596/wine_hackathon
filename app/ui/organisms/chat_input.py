import random
import string
import customtkinter as ctk
import tkinter.filedialog as fd
from ui.atoms.button import Button
from utils.image import path_to_image
from utils.core.encoding import encode_image_to_latent
from utils.core.encryption import encrypt_latent, encrypt_with_RSAKey
from states.friends_store import FriendsStore
from states.user_store import UserStore
from controllers.friend_controller import FriendController

class ChatInput(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.configure(fg_color="white", corner_radius=0)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.is_encoding = False

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
        path = fd.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if path:
            self.selected_file = path

            friend = FriendsStore().selected_friend

            # encode
            self.is_encoding = True
            self.file_button.configure(text="Encoding...")
            self.send_button.configure(state='disabled')
            
            image = path_to_image(self.selected_file)
            latent_tensor = encode_image_to_latent(image)
            
            # encrypt latent
            self.seed_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            self.enc_latent_tensor = encrypt_latent(latent_tensor, self.seed_string)
            
            # encrypt_seed
            self.enc_seed_bytes = encrypt_with_RSAKey(self.seed_string.encode('utf-8'), friend.public_key)

            self.is_encoding = False
            self.file_button.configure(text="File chosen")
            self.send_button.configure(state='normal')
        else:
            self.selected_file = None
            self.enc_latent_tensor = None
            self.enc_seed_string = None
            self.seed_string = None
            self.file_button.configure(text="Choose file")
            self.send_button.configure(state='normal')

    def send_message(self):
        text = self.textbox.get("0.0", "end").strip()
        if text:
            FriendController().send_text_message(
                UserStore().user_id,
                FriendsStore().selected_friend.friend_id,
                text
            )
            self.textbox.delete("0.0", "end")

        if self.selected_file and not self.is_encoding:
            FriendController().send_latent_message(
                UserStore().user_id,
                FriendsStore().selected_friend.friend_id,
                self.enc_latent_tensor,
                self.enc_seed_bytes,
                self.seed_string,
            )

            self.textbox.delete("0.0", "end")
            self.selected_file = None
            self.file_button.configure(text="Choose file")
