# 🍷 Wine Hackathon

## Overview

Today, as the world becomes increasingly connected through the internet, cybersecurity has emerged as a more critical issue than ever before. While many companies are striving to strengthen their security, completely preventing hacking remains a challenging task.

This project proposes an **AI-powered intelligent secure messenger system** to address these challenges. It ensures a high level of data security by utilizing **Edge AI encryption based on device-specific identifiers** during the image transmission process. Additionally, by compressing data in the latent domain before transmission, it minimizes data size and optimizes the use of communication resources.

### Key Features

1. **Edge AI-based encoding**  
   By sharing the same model parameters across clients, the target image is encoded into the latent domain in real time on the device. This allows only the compressed representation to be extracted without exposing the original image.

2. **Asymmetric key-based data encryption**  
   The generated latent vector is encrypted using a public key derived from a private key created on the user's device. This process ensures that only the intended recipient can decrypt the data.

3. **Encrypted Data Transmission and Interception Countermeasures**  
   The encrypted data is transmitted over the network, and even if it is intercepted during transmission, decryption is impossible, effectively preventing any actual information leakage. Additionally, the system verifies the device’s unique identifier (such as HW ID), ensuring that decryption is only possible on registered devices. This fundamentally blocks unauthorized decryption on unauthorized devices.

---

## Team Members

| 이름     | 이메일 |
|----------|--------|
| Sanghong Kim   | sanghongkim@korea.ac.kr |
| Byongho Lee   | unlike96@korea.ac.kr     |
| Kyeonghyun You   | seven1705@korea.ac.kr    |
| Geonwoo Kim   | bbosam2004@gmail.com     |
| Seungjoo Lee   | joon8958@gmail.com       |

---

## Dependencies

```text
Python >= 3.11  
pip >= 23.0
```

Python 3.11 or higher and pip 23.0 or higher are required. Additional libraries are specified in the requirements.txt file.


## Getting Started

### GUI Program
This is a GUI program that provides a chat-style user interface. Users can select a recipient from their friends list and upload image files to send encrypted messages.
1. **Navigate to the GUI directory from the project root**  
   ```bash
   cd app
   ```
2. **(Optional) Create and activate a virtual environment**
   * **venv Method**
   ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
   ``` 
   * **Anaconda Method**
   ```bash
    # Windows/Linux/Mac
    conda create -n wine_hackathon_app python=3.11
    conda activate wine_hackathon_app
   ```
3. **Install the required libraries.**  
   ```bash
    pip install -r requirements.txt
   ```
4. **Run the application.**  
   ```bash
    python main.py
   ```
5. **You can find the usage instructions in the tutorial video : https://youtu.be/6IaboUmv0tE**

### CLI Program
This is a CLI (Command Line Interface) program that provides functionality for encrypting and decrypting image files. It implements the core logic of the application, converting image files into encrypted latent vectors and allowing them to be decrypted.
1. **Navigate to the CLI directory from the project root.**  
   ```bash
   cd core
   ```
2. **(Optional) Create and activate a virtual environment.**
   * **venv Method**
   ```bash
    # Windows
    python -m venv venv
    source .\venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
   ``` 
   * **Anaconda Method**
   ```bash
    # Windows/Linux/Mac
    conda create -n wine_hackathon_core python=3.11
    conda activate wine_hackathon_core
   ```
3. **Install the required libraries.**  
   ```bash
    pip install -r requirements.txt
   ```
4. **Execute encryption.**
   The image is converted into a latent vector and saved as an encrypted file.
   - Input image file: `{input_image.png}`
   - Encryption key: `{key}` (A unique secret key entered by the user)
   - Encrypted latent vector file: `{encrypted_latent.pt}`
   ```bash
    python encrypt.py input_image.png --key={key}
   ```
5. **Execute decryption.**  
    The encrypted latent vector file is decrypted and restored to the original image.
    - Encrypted latent vector file: `{encrypted_latent.pt}`
    - Decryption key: `{key}` (The same key used during encryption)
    - Decrypted image file: `{reconstructed_image.png}`
   ```bash
    python decrypt.py encrypted_latent.pt --key={key}
   ```

## License
ChatGPT said:

This project is distributed under the MIT License. For more details, please refer to the LICENSE
 file.
