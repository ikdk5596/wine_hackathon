import torch
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
from utils.core.Encoder import Encoder
from utils.core.Decoder import Decoder

# Load Encoder and Decoder
torch_device = "cuda" if torch.cuda.is_available() else "cpu"

encoder = Encoder()
encoder.to(torch_device)

decoder = Decoder()
decoder.to(torch_device)

def encode_image_to_latent(image: Image.Image) -> torch.Tensor:
    # Preprocess the image
    if image.mode == 'RGBA':
        image = image.convert('RGB')
        
    transform = transforms.Compose([
        transforms.Resize((image.width, image.width)),  # Resize to square
        transforms.ToTensor(),
        transforms.Normalize([0.5] * 3, [0.5] * 3)
    ])
    image_tensor = transform(image).unsqueeze(0).to(torch_device) # Add batch dimension and move to device (1, C, H, W)

    # Encode the image to latent representation
    with torch.no_grad():
        latent = encoder(image_tensor).latents
    
    return latent


def decode_latent_to_image(latent: torch.Tensor) -> Image.Image:
    # Decode the latent representation to an image
    with torch.no_grad():
        decoded = decoder(latent)

    # Convert the tensor to a PIL image
    image_np = decoded.cpu().squeeze(0).permute(1, 2, 0).numpy()
    image_np = ((image_np + 1.0) / 2.0 * 255).clip(0, 255).astype(np.uint8)

    # Convert the numpy array to a PIL image
    return Image.fromarray(image_np)