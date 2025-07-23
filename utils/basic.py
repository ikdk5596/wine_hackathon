
"""
MIT License

Copyright (c) 2025 WINE Lab

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Authors: Sanghong Kim, Byungho Lee, Gunwoo Kim, Kyunghyun Yoo, Seungjoo Lee
"""

import torch
import numpy as np
import random
import torchvision.transforms as transforms
from PIL import Image


def set_seed(seed=42):
    """Set random seed for reproducibility"""
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def calculate_psnr(pred, target):
    """Calculate PSNR between predicted and target images"""
    mse = torch.mean((pred - target) ** 2)
    if mse == 0:
        return float('inf')
    max_pixel = 2.0  # [-1, 1] range
    psnr = 20 * torch.log10(max_pixel / torch.sqrt(mse))
    return psnr.item()


def pil_to_numpy(path, shape=None):
    # Convert a PIL image to normalized numpy array ([-1, 1] range)
    pil_img = Image.open(path).convert("RGB")
    if shape is not None:
        pil_img = pil_img.resize((shape, shape))
    tf = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.5]*3, [0.5]*3)
    ])
    tensor = tf(pil_img).unsqueeze(0)
    return tensor.numpy().astype(np.float32)


def numpy_to_pil(arr):
    # Convert a numpy array in [-1, 1] (1,3,H,W) or (3,H,W) to a PIL image
    if arr.ndim == 4:
        arr = arr[0]
    arr = arr.transpose(1,2,0)
    arr = (arr + 1.0) / 2.0
    arr = (arr * 255).clip(0,255).astype(np.uint8)
    return Image.fromarray(arr)


def preprocess_image(img_path, img_size=None):
    if img_size:
        transform = transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
    else:
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
    
    img = Image.open(img_path).convert('RGB')
    img_tensor = transform(img).unsqueeze(0)
    
    return img_tensor