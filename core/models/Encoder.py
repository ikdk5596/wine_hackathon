import torch
import torch.nn as nn
from diffusers.models import AutoencoderKL

class Encoder(nn.Module):
    """
    Encoder part of Stable Diffusion VAE (stabilityai/sd-vae-ft-ema)
    """
    def __init__(self, latent_dim=4):
        super().__init__()
        # Load pre-trained Stable Diffusion VAE
        self.vae = AutoencoderKL.from_pretrained(
            "stabilityai/sd-vae-ft-ema"
        )
        self.encoder = self.vae.encoder
        self.quant_conv = self.vae.quant_conv  # projects encoder output to latent_dim * 2

    def forward(self, x):
        """
        Args:
            x: Input image tensor (B, C, H, W) in [-1, 1] range
        Returns:
            mu, log_var, z, None (for VAE interface compatibility)
        """
        # Stable Diffusion VAE expects input in [-1, 1] range
        h = self.encoder(x)
        moments = self.quant_conv(h)
        mu, log_var = moments.chunk(2, dim=1)
        # VAE reparameterization trick
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        z = mu + eps * std
        
        return mu, log_var, z, None

    def reparameterize(self, mu, log_var):
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        return mu + eps * std
