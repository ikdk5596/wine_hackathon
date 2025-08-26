import os
import sys
import pathlib
import torch

# Path to the directory containing this setup.py (/app)
APP_DIR = pathlib.Path(__file__).resolve().parent
# Project root
PROJ_ROOT = APP_DIR.parent
# Path to the /core folder
CORE_DIR = PROJ_ROOT / "core"
# Output directory: /app/Models
MODELS_OUT_DIR = APP_DIR / "Models"

def _add_path(p: str) -> None:
    """Utility: add a path to sys.path so that Python can import modules from it"""
    p = os.path.abspath(p)
    if p not in sys.path:
        sys.path.insert(0, p)

def _load_models():
    """Dynamically import Encoder and Decoder classes from ../core/models"""
    _add_path(str(CORE_DIR))
    _add_path(str(CORE_DIR / "models"))

    # Try to load Encoder
    enc = None
    for mod, cls in [("models.Encoder", "Encoder"), ("Encoder", "Encoder")]:
        try:
            m = __import__(mod, fromlist=[cls])
            enc = getattr(m, cls)()   # instantiate Encoder()
            break
        except Exception:
            continue
    if enc is None:
        raise ImportError("Encoder not found in ../core/models")

    # Try to load Decoder
    dec = None
    for mod, cls in [("models.Decoder", "Decoder"), ("Decoder", "Decoder")]:
        try:
            m = __import__(mod, fromlist=[cls])
            dec = getattr(m, cls)()   # instantiate Decoder()
            break
        except Exception:
            continue
    if dec is None:
        raise ImportError("Decoder not found in ../core/models")

    return enc, dec

def main():
    # Default ONNX opset version
    opset = 17
    # Use CUDA if available, otherwise CPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load models
    encoder, decoder = _load_models()
    encoder = encoder.to(device).eval()
    decoder = decoder.to(device).eval()

    # Dummy input size (for tracing only, runtime supports dynamic shapes)
    H = W = 256
    dummy_img = torch.randn(1, 3, H, W, device=device)

    # Run a forward pass once to determine latent shape
    with torch.no_grad():
        latent = encoder(dummy_img)
        # Handle cases where encoder returns tuple/list/dict
        if isinstance(latent, (tuple, list)):
            latent = latent[0]
        if isinstance(latent, dict):
            latent = next(iter(latent.values()))
        latent = torch.as_tensor(latent, device=device)
        _ = decoder(latent)

    # Ensure output directory exists
    MODELS_OUT_DIR.mkdir(parents=True, exist_ok=True)
    enc_path = MODELS_OUT_DIR / "encoder.onnx"
    dec_path = MODELS_OUT_DIR / "decoder.onnx"

    # Dynamic axes for encoder ONNX export
    enc_dynamic_axes = {
        "image":  {0: "batch", 2: "height", 3: "width"},
        "latent": {0: "batch"},
    }
    # Dynamic axes for decoder ONNX export
    dec_dynamic_axes = {
        "latent": {0: "batch"},
        "image":  {0: "batch", 2: "height", 3: "width"},
    }
    # If latent is 4D (N, C, H, W), also make latent height/width dynamic
    if latent.dim() == 4:
        enc_dynamic_axes["latent"][2] = "latent_h"
        enc_dynamic_axes["latent"][3] = "latent_w"
        dec_dynamic_axes["latent"][2] = "latent_h"
        dec_dynamic_axes["latent"][3] = "latent_w"

    # Export encoder to ONNX
    torch.onnx.export(
        encoder,
        dummy_img,
        str(enc_path),
        export_params=True,
        opset_version=opset,
        do_constant_folding=True,
        input_names=["image"],
        output_names=["latent"],
        dynamic_axes=enc_dynamic_axes,
    )
    print(f"Saved: {enc_path}")

    # Export decoder to ONNX using dummy latent
    dummy_latent = torch.randn(*latent.shape, device=device)
    torch.onnx.export(
        decoder,
        dummy_latent,
        str(dec_path),
        export_params=True,
        opset_version=opset,
        do_constant_folding=True,
        input_names=["latent"],
        output_names=["image"],
        dynamic_axes=dec_dynamic_axes,
    )
    print(f"Saved: {dec_path}")
    print(f"traced latent shape: {tuple(latent.shape)}")

if __name__ == "__main__":
    main()
