import torch

import numpy as np
import hashlib
import argparse
import os

from models.Encoder import Encoder
from utils.basic import preprocess_image

def encrypt_image(image_path, user_key, image_size=None, num_rounds=8):
    """
    Encrypt image function
    
    Args:
        image_path (str): Path to image to encrypt
        user_key (str): Encryption key
        num_rounds (int): Number of encryption rounds
    
    Returns:
        torch.Tensor: Encrypted latent tensor
    """
    print(f"Starting encryption")
    
    # Load Encoder
    encoder = Encoder()
    torch_device = "cuda" if torch.cuda.is_available() else "cpu"
    encoder.to(torch_device)
    
    # Load input image
    print(f"Loading input image: {image_path}")
    input_image = preprocess_image(image_path, img_size=image_size).to(torch_device)
    
    # Encode to latent
    with torch.no_grad():
        _, _, latents, _ = encoder(input_image)  # (1, C, H, W)
    
    # Encrypt
    enc_latent = latents.clone()
    for i in range(num_rounds):
        round_key = f"{user_key}_{i}"
        seed = int(hashlib.sha256(round_key.encode('utf-8')).hexdigest(), 16) % (2**32)
        g = torch.Generator(device=latents.device).manual_seed(seed)
        noise = torch.randn(latents.shape, generator=g, device=latents.device)
        enc_latent = enc_latent + noise
    
    # Save encrypted latent as PT file
    torch.save(enc_latent.cpu(), "encrypted_latent.pt")
    print("Encrypted latent saved as encrypted_latent.pt")
    
    return enc_latent


def main():
    parser = argparse.ArgumentParser(description='Image Encryption')
    parser.add_argument('image_path', help='Path to image to encrypt')
    parser.add_argument('--key', required=True, help='Encryption key')
    parser.add_argument('--size', type=int, default=None, help='Image Size, if None use original size')
    parser.add_argument('--rounds', type=int, default=8, help='Number of encryption rounds (default: 8)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image_path):
        print(f"Error: Image file not found: {args.image_path}")
        return
    
    encrypt_image(args.image_path, args.key, args.rounds)
    print("Encryption completed!")


if __name__ == "__main__":
    main() 