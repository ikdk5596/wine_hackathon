import io
import base64
from PIL import Image

def path_to_base64(path) -> str:
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def path_to_image(path) -> Image.Image:
    with open(path, "rb") as image_file:
        return Image.open(io.BytesIO(image_file.read()))

def base64_to_image(b64_string: str | None) -> Image.Image:
    if b64_string is None:
        return None
    image_data = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(image_data))

def image_to_base64(image: Image.Image | None) -> str:
    if image is None:
        return None
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")