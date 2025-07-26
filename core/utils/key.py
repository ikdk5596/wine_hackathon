import torch
import hashlib
import numpy as np
import random


def generate_string_keys(batch_size, key_dim=8, device='cpu'):
    """Generate batch of string keys"""
    # Generate random string keys for each batch
    string_keys = []
    for i in range(batch_size):
        # Create a unique string key for each sample
        key_str = f"celeba_mnist_key_{i}_{random.randint(1000, 9999)}"
        string_keys.append(key_str)
    
    # Convert to tensor keys
    tensor_keys = batch_string_to_key(string_keys, key_dim, device)
    return tensor_keys, string_keys


def string_to_key(string_key, key_dim=8, device='cpu'):
    """
    Convert string key to tensor key
    
    Args:
        string_key: String input (e.g., "my_secret_key")
        key_dim: Dimension of the key tensor
        device: Device to place the tensor on
        
    Returns:
        torch.Tensor: Key tensor of shape (key_dim,)
    """
    # Create hash from string
    hash_object = hashlib.sha256(string_key.encode())
    hash_hex = hash_object.hexdigest()
    
    # Convert hex to numbers
    hash_numbers = []
    for i in range(0, len(hash_hex), 2):
        hash_numbers.append(int(hash_hex[i:i+2], 16))
    
    # Create key tensor
    key_tensor = torch.tensor(hash_numbers[:key_dim], dtype=torch.float32)
    
    # Normalize to [-1, 1] range
    key_tensor = (key_tensor / 255.0) * 2 - 1
    
    return key_tensor.to(device)


def key_to_string(key_tensor, precision=4):
    """
    Convert tensor key back to string representation
    
    Args:
        key_tensor: Key tensor
        precision: Number of decimal places to keep
        
    Returns:
        str: String representation of the key
    """
    # Convert to numpy and round
    key_np = key_tensor.detach().cpu().numpy()
    key_rounded = np.round(key_np, precision)
    
    # Convert to string
    key_str = "_".join([f"{x:.{precision}f}" for x in key_rounded])
    
    return key_str


def generate_random_key(key_dim=8, device='cpu'):
    """
    Generate a random key tensor
    
    Args:
        key_dim: Dimension of the key tensor
        device: Device to place the tensor on
        
    Returns:
        torch.Tensor: Random key tensor
    """
    return torch.randn(key_dim).to(device)


def batch_string_to_key(string_keys, key_dim=8, device='cpu'):
    """
    Convert batch of string keys to tensor keys
    
    Args:
        string_keys: List of string keys
        key_dim: Dimension of the key tensor
        device: Device to place the tensor on
        
    Returns:
        torch.Tensor: Key tensor of shape (batch_size, key_dim)
    """
    keys = []
    for key_str in string_keys:
        key_tensor = string_to_key(key_str, key_dim, device)
        keys.append(key_tensor)
    
    return torch.stack(keys)


if __name__ == "__main__":
    test_key = "my_secret_key_123"
    key_tensor = string_to_key(test_key, key_dim=8)
    print(f"String key: {test_key}")
    print(f"Key tensor: {key_tensor}")
    
    key_str = key_to_string(key_tensor)
    print(f"Key string: {key_str}")
    
    batch_keys = ["key1", "key2", "key3"]
    batch_tensor = batch_string_to_key(batch_keys, key_dim=8)
    print(f"Batch tensor shape: {batch_tensor.shape}") 