import torch.nn as nn
from diffusers.models import AutoencoderKL

class Decoder(nn.Module):
    """
    Decoder part of Stable Diffusion VAE (stabilityai/sd-vae-ft-ema)
    """
    def __init__(self, latent_dim=4, output_channels=3):
        super().__init__()
        self.vae = AutoencoderKL.from_pretrained(
            "stabilityai/sd-vae-ft-ema"
        )
        self.post_quant_conv = self.vae.post_quant_conv
        self.decoder = self.vae.decoder
        self.output_channels = output_channels

    def forward(self, z, skip_features=None):
        """
        Args:
            z: Latent tensor (B, latent_dim, H/8, W/8)
        Returns:
            x_reconstructed: Output image tensor (B, C, H, W) in [-1, 1] range
        """
        z = self.post_quant_conv(z)
        x_reconstructed = self.decoder(z)
        # Output is already in [-1, 1] range for sd-vae-ft-ema
        return x_reconstructed
