import customtkinter as ctk
from ui.atoms.input import Input
from ui.atoms.button import Button
from ui.atoms.link import Link
from ui.atoms.drag_drop import DragDrop
from ui.atoms.image_frame import ImageFrame
from ui.atoms.toast import Toast
from controllers.user_controller import UserController
import torch
import tkinter.filedialog as fd
from utils.core.encryption import decrypt_latent
from utils.core.encoding import decode_latent_to_image

class ViewerPage(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="#e0e0e0", **kwargs)
        self.controller = controller

        # center align frame
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # File picker button
        self.file_button = Button(self.center_frame, type="white", text="Choose file", command=self.pick_file, width=100)
        self.file_button.pack(pady=(10, 10))

        # image frame
        self.image_frame = ImageFrame(
            master=self.center_frame,
            image=None,  # Placeholder for the image
            width=256,
            height=256,
            border_radius=5
        )
        self.image_frame.pack(pady=(0, 20))


    # when a file is selected
    def pick_file(self):
        path = fd.askopenfilename(
                            filetypes=[("PyTorch Tensor", "*.pt"), ("All Files", "*.*")],
        )
        if path:
            self.selected_file = path
            self.file_button.configure(text="File Selected")
            
            # Load and display the image
            enc_latent_tensor = torch.load(path)
            latent_tensor = decrypt_latent(enc_latent_tensor, "your_seed_string")
            latent_image = decode_latent_to_image(latent_tensor)
            self.image_frame.update_image(latent_image)

            # self.image_frame.original_image