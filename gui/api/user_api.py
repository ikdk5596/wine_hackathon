import os
import json
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

USER_DB_PATH = "users.json"

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def _create_key_pair() -> tuple:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    return private_key, public_key

def _load_users() -> list:
    if not os.path.exists(USER_DB_PATH):
        return []
    with open(USER_DB_PATH, "r") as f:
        return json.load(f)

def _save_users(users: list):
    with open(USER_DB_PATH, "w") as f:
        json.dump(users, f, indent=2)

# api
def create_user(user_id: str, password: str) -> dict:
    users = _load_users()
    for user in users:
        if user["user_id"] == user_id:
            return {
                "status": "error",
                "message": "User already exists"
            }
        
    print(f"Creating user: {user_id}")
    
    # Create a new key pair for the user
    private_key, public_key = _create_key_pair()
    private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    users.append({
        "user_id": user_id,
        "password": _hash_password(password),
        "private_key": private_key,
        "public_key": public_key,
        "profile_base64": None
    })
    _save_users(users)

    return {
        "status": "success",
        "message": "User created successfully",
        "user_id": user_id,
        "private_key": private_key,
        "public_key": public_key,
        "profile_base64": None
    }

def update_user_profile(user_id: str, profile_base64: str | None) -> dict:
    users = _load_users()
    for user in users:
        if user["user_id"] == user_id:
            user["profile_base64"] = profile_base64
            _save_users(users)
            return {
                "status": "success",
                "message": "Profile updated successfully",
                "user_id": user_id,
                "profile_base64": profile_base64
            }
        
    return {
        "status": "error",
        "message": "User not found"
    }

def authenticate_user(user_id: str, password: str) -> dict:
    users = _load_users()
    hashed = _hash_password(password)
    for user in users:
        if user["user_id"] == user_id and user["password"] == hashed:
            # Load the private key for the user
            private_key = serialization.load_pem_private_key(
                user["private_key"].encode('utf-8'),
                password=None
            )
            public_key = serialization.load_pem_public_key(
                user["public_key"].encode('utf-8')
            )
            return {
                "status": "success",
                "message": "Authentication successful",
                "user_id": user["user_id"],
                "password": user.get("password", None),
                "private_key": private_key,
                "public_key": public_key,
                "profile_base64": user.get("profile_base64", None)
            }
        
    return {
        "status": "error",
        "message": "Invalid user ID or password"
    }
