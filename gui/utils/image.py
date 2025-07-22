import io
import base64
from PIL import Image

def path_to_base64(path) -> str:
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def base64_to_image(b64_string) -> Image.Image:
    image_data = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(image_data))