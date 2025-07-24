import customtkinter as ctk
from ui.atoms.toast import Toast
from ui.atoms.button import Button
from ui.atoms.input import Input
from utils.core.encoding import decode_latent_to_image
from utils.core.encryption import decrypt_latent
from utils.image import latent_to_gray_image
from controllers.friend_controller import FriendController
from controllers.user_controller import UserController
from states.user_store import UserStore
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import io
from ui.atoms.image_frame import ImageFrame
from PIL import Image
import tkinter.filedialog as fd

class DecryptImage(ctk.CTkFrame):
    def __init__(self, master, message):
        super().__init__(master)
        self.configure(fg_color="white", corner_radius=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.message = message

        latent_image = latent_to_gray_image(message["enc_latent_tensor"])
        self.latent_image_label = ImageFrame( master=self, image=latent_image, width=256, height=256, border_radius=5)
        self.latent_image_label.pack(padx=40, pady=(20, 10))

        buffer = io.BytesIO()
        self.latent_image_label.original_image.save(buffer, format="PNG")
        size_kb = len(buffer.getvalue()) / 1024  # size in KB
        self.size_label = ctk.CTkLabel(self, text=f"Size: {size_kb:.0f} KB", font=("Helvetica", 16), text_color="gray")
        self.size_label.pack(pady=(0, 10))

        self.entry = Input(self, placeholder="Password", show="•")
        self.entry.pack(pady=(10, 10))

        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.columnconfigure(0, weight=1)
        self.buttons_frame.columnconfigure(1, weight=1)
        self.buttons_frame.pack(pady=(0, 30))

        self.decrypt_button = Button(self.buttons_frame, text="Decrypt", command=self.decrypt)
        self.decrypt_button.grid(row=0, column=0, padx=(0, 5))

        self.save_button = Button(self.buttons_frame, type="white", text="Save Image", command=self.save_image)
        self.save_button.grid(row=0, column=1, padx=(5, 0))

    def decrypt(self):
        try:
            # authentication
            seed_string = 'wrong-seed'
            result = UserController().login(UserStore().user_id, self.entry.get())
            if result['status'] == 'success':
                # decrypt seed
                enc_seed_bytes = self.message["enc_seed_bytes"]
                seed_bytes = UserStore().private_key.decrypt(
                    enc_seed_bytes,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                seed_string = seed_bytes.decode('utf-8')  # Ensure seed is a string
            # decrypt latent tensor
            latent_tensor = decrypt_latent(self.message['enc_latent_tensor'], seed_string)
            decoded_image = decode_latent_to_image(latent_tensor)
            self.latent_image_label.configure(image=ctk.CTkImage(dark_image=decoded_image, size=(256, 256)))
            self.latent_image_label.pack(pady=(20, 10))

            # update image size
            buffer = io.BytesIO()
            decoded_image.save(buffer, format="PNG")
            size_kb = len(buffer.getvalue()) / 1024  # size in KB
            self.size_label.configure(text=f"Size: {size_kb:.0f} KB")
        except Exception as e:
            Toast(self, f"Authentication failed: {str(e)}", type="error", duration=2000)
            return
        
        self.entry.clear()

    def save_image(self):
        try:
            decoded_image = self.latent_image_label.original_image
            file_path = fd.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")], initialfile="decrypted_image.png")
            if file_path:
                decoded_image.save(file_path)
                Toast(self, "Image saved successfully!", type="success", duration=2000)
        except Exception as e:
            Toast(self, f"Error saving image: {str(e)}", type="error", duration=2000)