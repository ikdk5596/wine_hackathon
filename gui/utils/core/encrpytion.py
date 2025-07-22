import torch
import hashlib

def encrypt_latent(latent: torch.Tensor, user_key: str, num_rounds: int = 8) -> torch.Tensor:
    encrypted = latent.clone()
    for i in range(num_rounds):
        seed = int(hashlib.sha256(f"{user_key}_{i}".encode()).hexdigest(), 16) % (2**32)
        g = torch.Generator(device=latent.device).manual_seed(seed)
        noise = torch.randn(latent.shape, generator=g, device=latent.device)
        encrypted += noise
    return encrypted

def decrypt_latent(encrypted_latent: torch.Tensor, user_key: str, num_rounds: int = 8) -> torch.Tensor:
    decrypted = encrypted_latent.clone()
    for i in reversed(range(num_rounds)):
        seed = int(hashlib.sha256(f"{user_key}_{i}".encode()).hexdigest(), 16) % (2**32)
        g = torch.Generator(device=decrypted.device).manual_seed(seed)
        noise = torch.randn(decrypted.shape, generator=g, device=decrypted.device)
        decrypted -= noise
    return decrypted

