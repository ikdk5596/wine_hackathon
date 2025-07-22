import torch
from diffusers import VQModel
import torchvision.transforms as transforms
import PIL.Image
import numpy as np

vqvae = VQModel.from_pretrained("CompVis/ldm-celebahq-256", subfolder="vqvae")
torch_device = "cuda" if torch.cuda.is_available() else "cpu"
vqvae.to(torch_device)

def encode_image_to_latent(image: PIL.Image.Image) -> torch.Tensor:
    # Preprocess the image
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize([0.5] * 3, [0.5] * 3)
    ])
    image_tensor = transform(image).unsqueeze(0).to(torch_device) # Add batch dimension and move to device (1, C, H, W)

    # Encode the image to latent representation
    with torch.no_grad():
        latent = vqvae.encode(image_tensor).latents\
    
    return latent


def decode_latent_to_image(latent: torch.Tensor) -> PIL.Image.Image:
    # Decode the latent representation to an image
    with torch.no_grad():
        recon = vqvae.decode(latent).sample

    # Convert the tensor to a PIL image
    image_np = recon.cpu().squeeze(0).permute(1, 2, 0).numpy()
    image_np = ((image_np + 1.0) / 2.0 * 255).clip(0, 255).astype(np.uint8)

    # Convert the numpy array to a PIL image
    return PIL.Image.fromarray(image_np)

def visualize_latent(latent: torch.Tensor) -> PIL.Image.Image:
    # Visualize the latent representation as an RGB image
    latent_vis = latent.cpu().squeeze(0).mean(0)  # Average across channels
    rgb_vis = latent_vis.unsqueeze(0).repeat(3, 1, 1)  # Repeat to create RGB channels
    vis_np = (rgb_vis.permute(1, 2, 0) - latent_vis.min()) / (latent_vis.max() - latent_vis.min())
    vis_np = (vis_np.numpy() * 255).clip(0, 255).astype(np.uint8)

    return PIL.Image.fromarray(vis_np)