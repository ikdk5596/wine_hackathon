import torch
import torch.nn as nn
from .Encoder import Encoder
from .Decoder import Decoder

class VAE(nn.Module):
    """
    VAE model using Stable Diffusion VAE (stabilityai/sd-vae-ft-ema)
    """
    def __init__(self, latent_dim=4, output_channels=3):
        super().__init__()
        self.encoder = Encoder(latent_dim=latent_dim)
        self.decoder = Decoder(latent_dim=latent_dim, output_channels=output_channels)
        
    def forward(self, x, key=None):
        """
        Forward pass through VAE

        Args:
            x: Input images [B, C, H, W] in [-1, 1] range
            key: (옵션) 잠재 공간 조작용 key

        Returns:
            dict with mu, log_var, z, x_final (재구성 이미지)
        """
        mu, log_var, z, skip_features = self.encoder(x)
        
        x_reconstructed = self.decoder(z, skip_features)
        return {
            'mu': mu,
            'log_var': log_var,
            'z': z,
            'x_final': x_reconstructed
        }

    def encode(self, x):
        return self.encoder(x)

    def decode(self, z, skip_features=None):
        return self.decoder(z, skip_features)
