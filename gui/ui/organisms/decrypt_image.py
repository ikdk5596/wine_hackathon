import customtkinter as ctk
from ui.atoms.toast import Toast
from ui.atoms.button import Button
from ui.atoms.input import Input
from utils.core.encoding import visualize_latent, decode_latent_to_image
from utils.core.encryption import decrypt_latent
from controllers.friend_controller import FriendController
from controllers.user_controller import UserController
from states.user_store import UserStore
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import base64

class DecryptImage(ctk.CTkFrame):
    def __init__(self, master, message):
        super().__init__(master)
        self.configure(fg_color="white", corner_radius=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.message = message

        latent_image = visualize_latent(message["latent_tensor"])
        tk_image = ctk.CTkImage(dark_image=latent_image, size=(256, 256))
        self.latent_image_label = ctk.CTkLabel(self, image=tk_image, text="")
        self.latent_image_label.pack(pady=(20, 10))

        self.entry = Input(self, placeholder="Password", show="•")
        self.entry.pack(pady=(20, 10))

        self.button = Button(self, text="Decrypt", command=self.decrypt)
        self.button.pack()

    def decrypt(self):
        # authentication
        try:
            result = UserController().login(UserStore().user_id, self.entry.get())
            if result['status'] == 'success':
                encrypted_seed = self.message["encrypted_seed"]
                encrypted_bytes = base64.b64decode(encrypted_seed)
                seed = UserStore().private_key.decrypt(
                    encrypted_bytes,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                seed = seed.decode('utf-8')  # Ensure seed is a string
                decrypted_latent = decrypt_latent(self.message['latent_tensor'], seed)
                decoded_image = decode_latent_to_image(decrypted_latent)
                self.latent_image_label.configure(image=ctk.CTkImage(dark_image=decoded_image, size=(256, 256)))
                self.latent_image_label.pack(pady=(20, 10))
            else:
                Toast(self, "Authentication failed", type="error", duration=2000)
                return
        except Exception as e:
            Toast(self, f"Authentication failed: {str(e)}", type="error", duration=2000)
            return