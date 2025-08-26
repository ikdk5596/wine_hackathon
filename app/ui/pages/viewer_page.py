import customtkinter as ctk
import numpy as np
import tkinter.filedialog as fd
from ui.atoms.button import Button
from ui.atoms.image_frame import ImageFrame
from utils.mac import get_mac_address
from utils.core.onnx_encryption import decrypt_latent
from utils.core.onnx_encoding import decode_latent_to_image

MAC_ADDRESS = get_mac_address()

class ViewerPage(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="#e0e0e0", **kwargs)
        self.controller = controller

        # center align frame
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # image frame
        self.image_frame = ImageFrame(
            master=self.center_frame,
            image=None,  # Placeholder for the image
            width=256,
            height=256,
            border_radius=5
        )
        self.image_frame.pack(pady=(30, 10))

        # File picker button
        self.file_button = Button(self.center_frame, type="white", text="Choose file", command=self.pick_file, width=100)
        self.file_button.pack(pady=(0, 20))

    # when a file is selected
    def pick_file(self):
        path = fd.askopenfilename(
            filetypes=[("NumPy Array", "*.npy"), ("All Files", "*.*")],
        )
        
        if path:
            self.selected_file = path
            self.file_button.configure(text="File Selected")
            
            # Load and display the image
            enc_latent_array = np.load(path)
            latent_array = decrypt_latent(enc_latent_array, MAC_ADDRESS)
            latent_image = decode_latent_to_image(latent_array)
            self.image_frame.update_image(latent_image)
