import customtkinter as ctk
from tkinter import filedialog
from ui.atoms.profile import Profile
from ui.atoms.button import Button
from ui.atoms.toast import Toast
from utils.image import path_to_image
from utils.ip import get_my_ip
from states.user_store import UserStore
from controllers.user_controller import UserController

class MyProfile(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="white", corner_radius=0, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        self.ip_label = ctk.CTkLabel(self, text=f"My IP : {get_my_ip()}", font=("Helvetica", 12), text_color="gray")
        self.ip_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(10, 0))

        self.profile = Profile(self, image=UserStore().profile_image, size=82)
        self.profile.grid(row=1, column=0, rowspan=2, padx=(16, 10), pady=10)

        self.id_label = ctk.CTkLabel(self, text=UserStore().user_id, font=("Helvetica", 14, "bold"), anchor="w")
        self.id_label.grid(row=1, column=1, columnspan=2, sticky="w")

        self.upload_button = Button(self, text="Upload picture", command=self.upload_picture)
        self.upload_button.grid(row=2, column=1, sticky="w", padx=(0, 0), pady=(0, 0))

        self.delete_button = Button(self, type="white", text="Delete", command=self.delete_picture)
        self.delete_button.grid(row=2, column=2, sticky="w", padx=(12, 0), pady=(0, 0))
        if not UserStore().profile_image:
            self.delete_button.grid_remove()

        UserStore().add_observer("user_id", self._on_user_id_change)
        UserStore().add_observer("profile_image", self._on_profile_image_change)

    def upload_picture(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            try:
                result = UserController().update_profile_image(UserStore().user_id, path_to_image(file_path))
                if result['status'] == 'success':
                    Toast(self, result['message'], type="success", duration=2000)
                    self.upload_button.configure(text="Upload picture")
                    self.delete_button.grid()
                else:
                    Toast(self, result['message'], type="error", duration=2000)
            except Exception as e:
                Toast(self, f"Error: {str(e)}", type="error", duration=2000)


    def delete_picture(self):
        try:
            result = UserController().update_profile_image(UserStore().user_id, None)
            if result['status'] == 'success':
                Toast(self, result['message'], type="success", duration=2000)
                self.upload_button.configure(text="Upload picture")
                self.delete_button.grid_remove()
            else:
                Toast(self, result['message'], type="error", duration=2000)
        except Exception as e:
            Toast(self, f"Error: {str(e)}", type="error", duration=2000)

    def _on_profile_image_change(self):
        self.profile.update_image(UserStore().profile_image)

    def _on_user_id_change(self):
        self.id_label.configure(text=UserStore().user_id)
        self.ip_label.configure(text=f"My IP : {get_my_ip()}")
        self.profile.update_image(UserStore().profile_image)
        if UserStore().profile_image:
            self.upload_button.configure(text="Upload picture")
            self.delete_button.grid()
        else:
            self.upload_button.configure(text="Upload picture")
            self.delete_button.grid_remove()