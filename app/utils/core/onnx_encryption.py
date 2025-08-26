import numpy as np
import hashlib

def encrypt_latent(latent: list, key: str, num_rounds: int = 8) -> np.ndarray:
    encrypted = np.array(latent)
    for i in range(num_rounds):
        seed = int(hashlib.sha256(f"{key}_{i}".encode()).hexdigest(), 16) % (2**32)
        rng = np.random.default_rng(seed)
        noise = rng.standard_normal(size=encrypted.shape)
        encrypted += noise
    print(encrypted.shape)
    return encrypted


def decrypt_latent(encrypted_latent: np.ndarray, key: str, num_rounds: int = 8) -> np.ndarray:
    decrypted = encrypted_latent
    for i in reversed(range(num_rounds)):
        seed = int(hashlib.sha256(f"{key}_{i}".encode()).hexdigest(), 16) % (2**32)
        rng = np.random.default_rng(seed)
        noise = rng.standard_normal(size=decrypted.shape)
        decrypted -= noise
    return decrypted