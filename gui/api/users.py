import json
import os
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

def register_user(user_id: str, password: str) -> bool:
    users = _load_users()
    for user in users:
        if user["user_id"] == user_id:
            return False    # User already exists
        
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
        "profile": None
    })
    _save_users(users)
    return True

def update_profile(user_id: str, profile: str) -> bool:
    users = _load_users()
    for user in users:
        if user["user_id"] == user_id:
            user["profile"] = profile
            _save_users(users)
            return True
    return False

def authenticate_user(user_id: str, password: str) -> bool | dict:
    users = _load_users()
    hashed = _hash_password(password)
    for user in users:
        if user["user_id"] == user_id and user["password"] == hashed:
            private_key = serialization.load_pem_private_key(
                user["private_key"].encode('utf-8'),
                password=None
            )
            public_key = serialization.load_pem_public_key(
                user["public_key"].encode('utf-8')
            )
            return {
                "user_id": user["user_id"],
                "password": user.get("password", None),
                "private_key": private_key,
                "public_key": public_key,
                "profile": user.get("profile", None)
            }
    return False
