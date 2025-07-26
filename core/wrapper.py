import torch

class EncoderWrapper(torch.nn.Module):
    def __init__(self, vae):
        super().__init__()
        self.vae = vae
        
    def forward(self, x):
        # For SD VAEs: .encode(x).latent_dist.sample() gives latents for typical use
        return self.vae.encode(x).latent_dist.sample()
    
class DecodeWrapper(torch.nn.Module):
    def __init__(self, vae):
        super().__init__()
        self.vae = vae
        
    def forward(self, x):
        return self.vae.decode(x).sample
