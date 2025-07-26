import torch
import PIL.Image
import numpy as np
import hashlib
import argparse
import os

from models.Decoder import Decoder

def decrypt_image(encrypted_latent_path, user_key, num_rounds=8):
    """
    Decrypt encrypted latent function
    
    Args:
        encrypted_latent_path (str): Path to encrypted latent PT file
        user_key (str): Decryption key
        num_rounds (int): Number of decryption rounds
    
    Returns:
        torch.Tensor: Decrypted image tensor
    """
    print(f"Starting decryption")
    
    # Load Decoder
    decoder = Decoder()
    torch_device = "cuda" if torch.cuda.is_available() else "cpu"
    decoder.to(torch_device)
    
    # Load encrypted latent from PT file
    if not os.path.exists(encrypted_latent_path):
        print(f"Error: Encrypted latent file not found: {encrypted_latent_path}")
        return None
    
    enc_latent = torch.load(encrypted_latent_path)
    print(f"Loaded encrypted latent: {enc_latent.shape}")
    
    # Move encrypted latent to correct device
    enc_latent = enc_latent.to(torch_device)
    
    # Decrypt
    dec_latent = enc_latent.clone()
    for i in reversed(range(num_rounds)):
        round_key = f"{user_key}_{i}"
        seed = int(hashlib.sha256(round_key.encode('utf-8')).hexdigest(), 16) % (2**32)
        g = torch.Generator(device=enc_latent.device).manual_seed(seed)
        noise = torch.randn(enc_latent.shape, generator=g, device=enc_latent.device)
        dec_latent = dec_latent - noise
    
    # Decode decrypted latent
    with torch.no_grad():
        decoded = decoder(dec_latent)
    
    # Save reconstructed image
    image_np = decoded.cpu().squeeze(0).permute(1, 2, 0).numpy()
    image_np = (image_np + 1.0) / 2.0
    image_np = (image_np * 255).clip(0, 255).astype(np.uint8)
    image_pil = PIL.Image.fromarray(image_np)
    image_pil.save("reconstructed_image.png")
    print("Reconstructed image saved as reconstructed_image.png")
    
    return decoded


def main():
    parser = argparse.ArgumentParser(description='Image Decryption')
    parser.add_argument('encrypted_latent_path', help='Path to encrypted latent PT file')
    parser.add_argument('--key', required=True, help='Decryption key')
    parser.add_argument('--rounds', type=int, default=8, help='Number of decryption rounds (default: 8)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.encrypted_latent_path):
        print(f"Error: Encrypted latent file not found: {args.encrypted_latent_path}")
        return
    
    decrypt_image(args.encrypted_latent_path, args.key, args.rounds)
    print("Decryption completed!")


if __name__ == "__main__":
    main()