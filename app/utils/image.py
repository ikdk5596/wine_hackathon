import io
import base64
from PIL import Image
import numpy as np

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

def latent_to_gray_image(latent: np.ndarray) -> Image.Image:
    if latent.ndim == 4 and latent.shape[0] == 1:
        latent = latent[0]  # shape: (C, H, W)
    latent_vis = latent.mean(axis=0)  # shape: (H, W)
    rgb_vis = np.stack([latent_vis] * 3, axis=-1)  # shape: (H, W, 3)
    min_val, max_val = latent_vis.min(), latent_vis.max()
    if max_val - min_val == 0:
        vis_np = np.zeros_like(rgb_vis, dtype=np.uint8)
    else:
        vis_np = ((rgb_vis - min_val) / (max_val - min_val) * 255).clip(0, 255).astype(np.uint8)
    return Image.fromarray(vis_np)