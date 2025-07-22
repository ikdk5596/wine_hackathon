import customtkinter as ctk
from PIL import Image, ImageDraw
import os

DEFAULT_IMAGE_PATH = "assets/images/default_user.png"

class Profile(ctk.CTkLabel):
    def __init__(self, master, image=None, size=60):
        self.size = size
        super().__init__(master, text="")
        self.update_image(image)

    def update_image(self, pil_image: Image.Image | None):
        if pil_image is None:
            pil_image = Image.open(DEFAULT_IMAGE_PATH)

        # 원형 마스크 적용
        mask = Image.new("L", (self.size, self.size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, self.size, self.size), fill=255)

        pil_image = pil_image.resize((self.size, self.size)).convert("RGBA")
        pil_image.putalpha(mask)

        # CTkImage로 변환 후 설정
        ctk_img = ctk.CTkImage(pil_image, size=(self.size, self.size))
        self.configure(image=ctk_img)
