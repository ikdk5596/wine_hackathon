import customtkinter as ctk
from PIL import Image, ImageDraw

DEFAULT_IMAGE_PATH = "assets/images/default_user.png"

class Profile(ctk.CTkLabel):
    def __init__(self, master, image=None, size=60):
        super().__init__(master, text="")
        self.size = size

        self.update_image(image)

    def update_image(self, pil_image: Image.Image | None):
        self.original_image = pil_image if pil_image else Image.open(DEFAULT_IMAGE_PATH)

        # circle mask
        mask = Image.new("L", (self.size, self.size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, self.size, self.size), fill=255)

        pil_image = self.original_image.resize((self.size, self.size)).convert("RGBA")
        pil_image.putalpha(mask)

        # show image
        ctk_image = ctk.CTkImage(pil_image, size=(self.size, self.size))
        self.configure(image=ctk_image)
