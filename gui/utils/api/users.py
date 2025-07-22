import json
import os
import hashlib

USER_DB_PATH = "users.json"

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def _load_users() -> list:
    if not os.path.exists(USER_DB_PATH):
        return []
    with open(USER_DB_PATH, "r") as f:
        return json.load(f)

def _save_users(users: list):
    with open(USER_DB_PATH, "w") as f:
        json.dump(users, f, indent=2)

def register_user(user_id: str, password: str) -> str:
    users = _load_users()
    for user in users:
        if user["user_id"] == user_id:
            return False    # User already exists
    users.append({
        "user_id": user_id,
        "password": _hash_password(password)
    })
    _save_users(users)
    return True

def authenticate_user(user_id: str, password: str) -> bool:
    users = _load_users()
    hashed = _hash_password(password)
    for user in users:
        if user["user_id"] == user_id and user["password"] == hashed:
            return True
    return False
