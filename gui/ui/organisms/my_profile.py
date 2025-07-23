import customtkinter as ctk
import socket
from tkinter import filedialog
from ui.atoms.profile import Profile
from ui.atoms.button import Button
from utils.image import path_to_base64
from states.user_store import UserStore

class MyProfile(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="white", corner_radius=0, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.ip_label = ctk.CTkLabel(self, text=f"My IP : {self._get_ip()}", font=("Helvetica", 12), text_color="gray")
        self.ip_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(10, 0))

        self.profile = Profile(self, image=UserStore().profile, size=82)
        self.profile.grid(row=1, column=0, rowspan=2, padx=(16, 10), pady=10)

        self.id_label = ctk.CTkLabel(self, text=UserStore().user_id, font=("Helvetica", 14, "bold"), anchor="w")
        self.id_label.grid(row=1, column=1, columnspan=2, sticky="w")

        self.upload_button = Button(self, text="Upload picture", command=self.upload_picture)
        self.upload_button.grid(row=2, column=1, sticky="w", padx=(0, 0), pady=(0, 0))

        self.delete_button = Button(self, text="Delete", command=self.delete_picture)
        self.delete_button.grid(row=2, column=2, sticky="w", padx=(12, 0), pady=(0, 0))
        if not UserStore().profile:
            self.delete_button.grid_remove()

        user_store_instance = UserStore()
        user_store_instance.add_observer("profile", self._on_profile_change)

    def reset(self):
        self.profile.update_image(UserStore().profile)
        self.id_label.configure(text=UserStore().user_id)
        self.ip_label.configure(text=f"My IP : {self._get_ip()}")
        if UserStore().profile:
            self.upload_button.configure(text="Upload new picture")
            self.delete_button.grid()
        else:
            self.upload_button.configure(text="Upload picture")
            self.delete_button.grid_remove()

    def _get_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "0.0.0.0"

    def upload_picture(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            UserStore().update_picture(path_to_base64(file_path))

            self.upload_button.configure(text="Upload new picture")
            self.delete_button.grid()

    def delete_picture(self):
        UserStore().update_picture(None)

        self.upload_button.configure(text="Upload picture")
        self.delete_button.grid_remove()

    def _on_profile_change(self):
        self.profile.update_image(UserStore().profile)