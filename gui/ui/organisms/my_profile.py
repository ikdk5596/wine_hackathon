import customtkinter as ctk
from tkinter import filedialog
from ui.atoms.profile import Profile
from ui.atoms.button import Button
from ui.atoms.toast import Toast
from utils.image import path_to_image
from utils.network import get_my_ip, get_my_port
from states.user_store import UserStore
from controllers.user_controller import UserController

class MyProfile(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="white", corner_radius=0, **kwargs)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        userStore = UserStore()

        self.ip_label = ctk.CTkLabel(self, text=f"My IP : {get_my_ip()}   /   Port : {get_my_port()}", font=("Helvetica", 12), text_color="gray")
        self.ip_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(10, 0))

        self.profile = Profile(self, image=userStore.profile_image, size=82)
        self.profile.grid(row=1, column=0, rowspan=2, padx=(16, 13), pady=10)

        self.id_label = ctk.CTkLabel(self, text=userStore.user_id, font=("Helvetica", 15, "bold"), anchor="w")
        self.id_label.grid(row=1, column=1, columnspan=2, padx=(2, 0), pady=(10, 0), sticky="w")

        self.upload_button = Button(self, text="Upload picture", command=self.upload_picture)
        self.upload_button.grid(row=2, column=1, sticky="w", padx=(0, 0), pady=(0, 10))

        self.delete_button = Button(self, type="white", text="Delete", command=self.delete_picture)
        self.delete_button.grid(row=2, column=2, sticky="w", padx=(12, 0), pady=(0, 10))
        if userStore.profile_image:
            self.delete_button.grid()
        else:
            self.delete_button.grid_remove()
            
        userStore.add_observer("user_id", self._on_user_id_change)
        userStore.add_observer("profile_image", self._on_profile_image_change)

    def upload_picture(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            try:
                result = UserController().update_profile_image(UserStore().user_id, path_to_image(file_path))
                if result['status'] == 'success':
                    Toast(self.controller, result['message'], type="success", duration=2000)
                    self.delete_button.grid()
                else:
                    Toast(self.controller, result['message'], type="error", duration=2000)
            except Exception as e:
                Toast(self.controller, f"Error: {str(e)}", type="error", duration=2000)

    def delete_picture(self):
        try:
            result = UserController().update_profile_image(UserStore().user_id, None)
            if result['status'] == 'success':
                Toast(self.controller, result['message'], type="success", duration=2000)
                self.delete_button.grid_remove()
            else:
                Toast(self.controller, result['message'], type="error", duration=2000)
        except Exception as e:
            Toast(self, f"Error: {str(e)}", type="error", duration=2000)

    def _on_profile_image_change(self):
        userStore = UserStore()
        self.profile.update_image(userStore.profile_image)
        if userStore.profile_image:
            self.delete_button.grid()
        else:
            self.delete_button.grid_remove()

    def _on_user_id_change(self):
        userStore = UserStore()

        self.id_label.configure(text=userStore.user_id)
        self.ip_label.configure(text=f"My IP : {get_my_ip()}   /   Port : {get_my_port()}")
        self.profile.update_image(userStore.profile_image)

        if userStore.profile_image:
            self.delete_button.grid()
        else:
            self.delete_button.grid_remove()