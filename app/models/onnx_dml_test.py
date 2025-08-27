import numpy as np
import cv2
import hashlib
import time
import onnxruntime as ort

SIZE = 256
KEY = 'constant'


def encode(img_path: str) -> np.ndarray:
    img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Failed to read image: {img_path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (SIZE, SIZE), interpolation=cv2.INTER_LINEAR)
    img = img.astype(np.float32) / 255.0
    img = (img * 2.0 - 1.0).transpose(2, 0, 1)[None, ...]

    session = ort.InferenceSession('encoder.onnx', providers=["DmlExecutionProvider"])
    
    outputs = session.get_outputs()[0].name
    inputs = session.get_inputs()[0].name

    t0 = time.time()
    prediction = session.run([outputs], {inputs: img})
    t1 = time.time()
    print(f"✅ Encoding done in {t1 - t0:.3f} seconds")

    print('latent_shape', session.get_outputs()[0].shape)
    return prediction

def encrypt(latent: list, key: str, num_rounds: int = 8) -> np.ndarray:
    encrypted = np.array(latent)
    for i in range(num_rounds):
        seed = int(hashlib.sha256(f"{key}_{i}".encode()).hexdigest(), 16) % (2**32)
        rng = np.random.default_rng(seed)
        noise = rng.standard_normal(size=encrypted.shape)
        encrypted += noise
    print('enc', encrypted.shape)
    return encrypted[0]


def decrypt(encrypted_latent: np.ndarray, key: str, num_rounds: int = 8) -> np.ndarray:
    decrypted = encrypted_latent
    for i in reversed(range(num_rounds)):
        seed = int(hashlib.sha256(f"{key}_{i}".encode()).hexdigest(), 16) % (2**32)
        rng = np.random.default_rng(seed)
        noise = rng.standard_normal(size=decrypted.shape)
        decrypted -= noise
    print('dec', decrypted.shape)
    return decrypted

def decode(latent: np.ndarray) -> np.ndarray:
    session = ort.InferenceSession('decoder.onnx', providers=["DmlExecutionProvider"])
    
    outputs = session.get_outputs()[0].name
    inputs = session.get_inputs()[0].name

    print(latent.shape, session.get_inputs()[0].shape)
    t6 = time.time()
    prediction = session.run([outputs], {inputs: latent})
    t7 = time.time()
    print(f"✅ Decoding done in {t7 - t6:.3f} seconds")


    x = np.clip((prediction[0] + 1.0) * 0.5, 0.0, 1.0)[0]  # (3,H,W)
    # print(prex.shape)
    x = (x.transpose(1, 2, 0) * 255.0).round().astype(np.uint8)  # (H,W,3)

    return x

def main():
    input_image_path = 'input_image.png'
    output_image_path = 'output_image.png'

    print("🔄 Starting image encoding...")
    latent = encode(input_image_path)

    print("🔐 Encrypting latent...")
    t2 = time.time()
    enc_latent = encrypt(latent, KEY)
    t3 = time.time()
    print(f"✅ Encryption done in {t3 - t2:.3f} seconds")

    print("🔓 Decrypting latent...")
    t4 = time.time()
    dec_latent = decrypt(enc_latent, KEY)
    t5 = time.time()
    print(f"✅ Decryption done in {t5 - t4:.3f} seconds")

    print("🎨 Decoding image...")
    output_image = decode(dec_latent)

    cv2.imwrite('output_image.png', cv2.cvtColor(output_image, cv2.COLOR_RGB2BGR))
    print(f"📁 Image saved to {output_image_path}")

if __name__ == "__main__":
    main()