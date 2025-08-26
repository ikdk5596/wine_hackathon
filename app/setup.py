import os
import sys
import pathlib
import torch

# --- Paths ---
APP_DIR = pathlib.Path(__file__).resolve().parent        # /app
UTILS_CORE_DIR = APP_DIR / "utils" / "core"              # app/utils/core
MODELS_OUT_DIR = APP_DIR / "models"

# Candidate directories where Encoder/Decoder definitions may exist
CANDIDATE_MODEL_DIRS = [
    UTILS_CORE_DIR / "models",
    UTILS_CORE_DIR,
]

def _add_path(p: pathlib.Path):
    """Add a directory to sys.path if not already included."""
    p = str(p.resolve())
    if p not in sys.path:
        sys.path.insert(0, p)

def _try_import():
    """
    Try importing Encoder and Decoder classes from multiple candidate paths.
    Attempts both 'models.Encoder' and 'Encoder' (same for Decoder).
    Returns instantiated Encoder and Decoder objects.
    """
    for d in CANDIDATE_MODEL_DIRS:
        if d.exists():
            _add_path(d)
            _add_path(d.parent)

    def _import_one(kind):
        for mod, cls in [(f"models.{kind}", kind), (kind, kind)]:
            try:
                m = __import__(mod, fromlist=[cls])
                obj = getattr(m, cls)()
                return obj, mod
            except Exception:
                continue
        return None, None

    enc, enc_from = _import_one("Encoder")
    if enc is None:
        raise ImportError("Encoder class not found in any candidate paths.")

    dec, dec_from = _import_one("Decoder")
    if dec is None:
        raise ImportError("Decoder class not found in any candidate paths.")

    print(f"Encoder loaded from: {enc_from}")
    print(f"Decoder loaded from: {dec_from}")
    return enc, dec

def main():
    # ONNX opset version
    opset = 17
    # Select CUDA if available, otherwise CPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load models
    encoder, decoder = _try_import()
    encoder = encoder.to(device).eval()
    decoder = decoder.to(device).eval()

    H = W = 256
    dummy_img = torch.randn(1, 3, H, W, device=device)

    with torch.no_grad():
        latent = encoder(dummy_img)
        # Handle tuple/list/dict outputs
        if isinstance(latent, (tuple, list)):
            latent = latent[0]
        if isinstance(latent, dict):
            latent = next(iter(latent.values()))
        latent = torch.as_tensor(latent, device=device)
        _ = decoder(latent)

    MODELS_OUT_DIR.mkdir(parents=True, exist_ok=True)
    enc_path = MODELS_OUT_DIR / "encoder.onnx"
    dec_path = MODELS_OUT_DIR / "decoder.onnx"

    enc_axes = {"image": {0: "batch", 2: "height", 3: "width"},
                "latent": {0: "batch"}}

    dec_axes = {"latent": {0: "batch"},
                "image": {0: "batch", 2: "height", 3: "width"}}

    if latent.dim() == 4:
        enc_axes["latent"][2] = "latent_h"
        enc_axes["latent"][3] = "latent_w"
        dec_axes["latent"][2] = "latent_h"
        dec_axes["latent"][3] = "latent_w"

    # Export encoder
    torch.onnx.export(
        encoder, dummy_img, str(enc_path),
        export_params=True, opset_version=opset, do_constant_folding=True,
        input_names=["image"], output_names=["latent"], dynamic_axes=enc_axes,
    )
    print(f"Saved: {enc_path}")

    # Export decoder
    dummy_latent = torch.randn(*latent.shape, device=device)
    torch.onnx.export(
        decoder, dummy_latent, str(dec_path),
        export_params=True, opset_version=opset, do_constant_folding=True,
        input_names=["latent"], output_names=["image"], dynamic_axes=dec_axes,
    )
    print(f"Saved: {dec_path}")
    print(f"traced latent shape: {tuple(latent.shape)}")

if __name__ == "__main__":
    main()
