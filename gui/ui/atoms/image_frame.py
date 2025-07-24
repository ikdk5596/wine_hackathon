import customtkinter as ctk
from PIL import Image, ImageDraw

class ImageFrame(ctk.CTkFrame):
    def __init__(self, master, pil_image: Image.Image, width=200, height=200, border_radius=20, **kwargs):
        super().__init__(master, width=width, height=height, fg_color="transparent", **kwargs)
        self.border_radius = border_radius
        self.original_image = pil_image
        self.width = width
        self.height = height

        # 이미지 리사이즈 및 라운드 처리
        self.rounded_image = self._get_rounded_image(pil_image, width, height, border_radius)

        # CTkImage로 변환
        self.ctk_image = ctk.CTkImage(light_image=self.rounded_image, dark_image=self.rounded_image, size=(width, height))

        # 라벨에 이미지 표시
        self.image_label = ctk.CTkLabel(self, image=self.ctk_image, text="")
        self.image_label.place(x=0, y=0, width=width, height=height)

    def _get_rounded_image(self, img: Image.Image, width: int, height: int, radius: int) -> Image.Image:
        img = img.resize((width, height), Image.LANCZOS).convert("RGBA")

        # 마스크 생성
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=255)

        # 마스크 적용
        img.putalpha(mask)