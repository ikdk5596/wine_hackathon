import os
import time
import numpy as np
from PIL import Image
import onnxruntime as ort

SIZE = 256 # compiled with fixed size

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

encoder_path = os.path.join(BASE_DIR, '../../models/encoder.onnx')
decoder_path = os.path.join(BASE_DIR, '../../models/decoder.onnx')

encoder_session = ort.InferenceSession(encoder_path, providers=["DmlExecutionProvider"])
decoder_session = ort.InferenceSession(decoder_path, providers=["DmlExecutionProvider"])

def encode_image_to_latent(image: Image.Image) -> np.ndarray:
    """Convert a PIL image to latent tensor using encoder ONNX model."""
    # preprocess
    img = image.convert("RGB").resize((SIZE, SIZE), Image.LANCZOS)
    img_np = np.array(img).astype(np.float32) / 255.0  # (H,W,3)
    img_np = (img_np * 2.0 - 1.0).transpose(2, 0, 1)[None, ...]  # (1,3,H,W)

    # encoding
    input_name = encoder_session.get_inputs()[0].name
    output_name = encoder_session.get_outputs()[0].name

    t1 = time.time()
    latent = encoder_session.run([output_name], {input_name: img_np})[0]
    t2 = time.time()
    print(f"Encoding time: {t2 - t1:.4f} seconds")
    return latent  # shape: (1,C,H,W)

def decode_latent_to_image(latent: np.ndarray) -> Image.Image:
    """Convert latent tensor to PIL image using decoder ONNX model."""

    # decoding
    input_name = decoder_session.get_inputs()[0].name
    output_name = decoder_session.get_outputs()[0].name
    t1 = time.time()
    prediction = decoder_session.run([output_name], {input_name: latent})[0]
    t2 = time.time()
    print(f"Decoding time: {t2 - t1:.4f} seconds")
    
    # postprocess
    x = np.clip((prediction[0] + 1.0) * 0.5, 0.0, 1.0)  # (3,H,W)
    x = (x.transpose(1, 2, 0) * 255.0).round().astype(np.uint8)  # (H,W,3)
    return Image.fromarray(x)

