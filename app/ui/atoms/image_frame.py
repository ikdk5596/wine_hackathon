import customtkinter as ctk
from PIL import Image, ImageDraw

class ImageFrame(ctk.CTkLabel):
    def __init__(self, master, image: Image.Image, width=200, height=200, border_radius=20, **kwargs):
        super().__init__(master, text="", **kwargs)
        self.original_image = image
        self.width = width
        self.height = height
        self.border_radius = border_radius
        self.update_image(image)

    def update_image(self, image: Image.Image | None):
        self.image = image

        if image is None:
            gray_image = Image.new("RGB", (self.width, self.height), (200, 200, 200)) 
            image = gray_image

        # rounded rectangle mask
        mask = Image.new("L", (self.width, self.height), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, self.width, self.height), radius=self.border_radius, fill=255)

        pil_image = image.resize((self.width, self.height), Image.LANCZOS).convert("RGBA")
        pil_image.putalpha(mask)

        # show image
        ctk_image = ctk.CTkImage(pil_image, size=(self.width, self.height))
        self.configure(image=ctk_image)



    