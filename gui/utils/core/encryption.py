import torch
import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey

def encrypt_latent(latent: torch.Tensor, key: str, num_rounds: int = 8) -> torch.Tensor:
    encrypted = latent.clone()
    for i in range(num_rounds):
        seed = int(hashlib.sha256(f"{key}_{i}".encode()).hexdigest(), 16) % (2**32)
        g = torch.Generator(device=latent.device).manual_seed(seed)
        noise = torch.randn(latent.shape, generator=g, device=latent.device)
        encrypted += noise
    return encrypted

def decrypt_latent(encrypted_latent: torch.Tensor, key: str, num_rounds: int = 8) -> torch.Tensor:
    decrypted = encrypted_latent.clone()
    for i in reversed(range(num_rounds)):
        seed = int(hashlib.sha256(f"{key}_{i}".encode()).hexdigest(), 16) % (2**32)
        g = torch.Generator(device=decrypted.device).manual_seed(seed)
        noise = torch.randn(decrypted.shape, generator=g, device=decrypted.device)
        decrypted -= noise
    return decrypted

def encrypt_with_RSAKey(data: bytes, public_key: RSAPublicKey) -> bytes:
    encrypted_data = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_data

def decrypt_with_RSAKey(encrypted_data: bytes, private_key: RSAPrivateKey) -> bytes:
    decrypted_data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
