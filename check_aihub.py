import os
import argparse

# Pytorch implement
import torch
from diffusers.models import AutoencoderKL

# AI hub implement
import qai_hub as hub

# Custom implement
import wrapper
import utils

# Target Device is Snapdragon Elite X Plus Device -> from 
TARGET_DEVICE = "Snapdragon X Plus 8-Core CRD"


def get_latent_shape(model, size):
    """
    \nGet latent shape
    Args:
        model: vae model
        size: input image size
    Returns:
        latent shape (1, c, h, w)
    """
    dummy = torch.randn(1, 3, size, size)
    with torch.no_grad():
        latents = model.encode(dummy).latent_dist.sample()
    return latents.shape  # (1, c, h, w)


def compile_models(device, size, force=False):
    """
    \nCompile model on Qualcomm AI Hub
    Args:
        device: TARGET_DEVICE
        size: input image size
        force: force compile or not Option, default: False
    """
    
    # For saving encoder and decoder model at local storage
    enc_model_path = f"enc_{size}.qpc.onnx.zip"
    dec_model_path = f"dec_{size}.qpc.onnx.zip"
    
    # Skip compile when enc model and dec model exist.
    if not force and os.path.exists(enc_model_path) and os.path.exists(dec_model_path):
        print(f"[{size}] Compiled models already exist. Skipping compilation.")
        return

    print(f"[{size}] Compiling encoder/decoder models...")
    
    # Using SD-VAE, It is a model used at Stable Diffusion
    model = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-ema").eval()
    
    enc_wrap = wrapper.EncoderWrapper(model).eval()
    dec_wrap = wrapper.DecodeWrapper(model).eval()
    
    # Dummy image for trace model
    dummy_img = torch.randn(1, 3, size, size)
    latent_shape = get_latent_shape(model, size)
    dummy_latent = torch.randn(*latent_shape)

    # Compile encoder
    traced_enc = torch.jit.trace(enc_wrap, dummy_img)
    enc_job = hub.submit_compile_job(
        model=traced_enc,
        device=device,
        name=f"VAE encoder {size}",
        input_specs=dict(image=(1, 3, size, size))
    )
    enc_job.wait()
    enc_job.download_target_model(enc_model_path)

    # Compile decoder
    traced_dec = torch.jit.trace(dec_wrap, dummy_latent)
    _, c, h, w = latent_shape
    dec_job = hub.submit_compile_job(
        model=traced_dec,
        device=device,
        name=f"VAE decoder {size}",
        input_specs=dict(latent=(1, c, h, w))
    )
    dec_job.wait()
    dec_job.download_target_model(dec_model_path)
    
    print(f"[{size}] Model compilation completed.")
    
    
def profile_model(device, size):
    """
    \nProfile model on Qualcomm AI Hub
    Args:
        device: TARGET_DEVICE
        size: input image size
    """
    
    # load encoder and decoder model
    enc_model_path = f"enc_{size}.qpc.onnx.zip"
    dec_model_path = f"dec_{size}.qpc.onnx.zip"
    
    # Profile encoder
    encoder_profile_job = hub.submit_profile_job(
        model=enc_model_path,
        device=device,
        name=f"VAE encoder {size}"
    )
    encoder_profile_job.wait()
    
    # Profile Decoder
    decoder_profile_job = hub.submit_profile_job(
        model=dec_model_path,
        device=device,
        name=f"VAE decoder {size}"
    )
    decoder_profile_job.wait()
    

def run_inference(device, size, input_image):
    """
    \nProfile model on Qualcomm AI Hub
    Args:
        device: TARGET_DEVICE
        size: input image size
        input_img: input image (numpy type)
    """
    # load encoder and decoder model
    enc_model_path = f"enc_{size}.qpc.onnx.zip"
    dec_model_path = f"dec_{size}.qpc.onnx.zip"
    
    input_list = [input_image]

    # Inference encoder
    enc_infer_job = hub.submit_inference_job(
        enc_model_path,
        device,
        {"x": input_list}
    )
    
    enc_infer_job.wait()
    enc_latent = enc_infer_job.download_output_data()
    
    # handle laten
    if isinstance(enc_latent, dict):
        latent = list(enc_latent.values())[0]
    else:
        latent = enc_latent
        
    if isinstance(latent, list):
        latent = latent[0]
        
    print(f"[{size}] Latent shape:", latent.shape)

    # Decoder
    latent_list = [latent]
    
    dec_infer_job = hub.submit_inference_job(
        dec_model_path,
        device,
        {"x": latent_list}
    )
    
    dec_infer_job.wait()
    dec_img = dec_infer_job.download_output_data()
    
    if isinstance(dec_img, dict):
        decoded = list(dec_img.values())[0]
    else:
        decoded = dec_img
        
    if isinstance(decoded, list):
        decoded = decoded[0]
        
    print(f"[{size}] Decoded image shape:", decoded.shape)
    
    return decoded


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sizes', type=int, nargs='+', default=[256],
                        help='List of image sizes to test (e.g., --sizes 256 512)')
    parser.add_argument('--image', type=str, default="input_image.png",
                        help='Input image path')
    parser.add_argument('--force', action='store_true', help='Force recompilation of models')
    args = parser.parse_args()
    
    device = hub.Device(TARGET_DEVICE)

    for size in args.sizes:
        print(f"\n=== Testing image size {size} ===")
        compile_models(device, size, force=args.force)

        try:
            profile_model(device, size)
        except Exception as e:
            print(f"[{size}] Error during profiling: {e}")

        try:
            input_image = utils.basic.pil_to_numpy(args.image, size)
        except Exception as e:
            print(f"[{size}] Error loading input image: {e}")
            continue
        
        try:
            decoded = run_inference(device, size, input_image)
            out_img = utils.basic.numpy_to_pil(decoded)
            out_img.save(f"output_{args.model}_{size}.png")
            print(f"[{size}] Reconstructed image saved as: output_{size}.png")
        except Exception as e:
            print(f"[{size}] Error during inference or saving the result: {e}")

if __name__ == "__main__":
    main()