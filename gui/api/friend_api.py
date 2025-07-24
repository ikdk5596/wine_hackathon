import time
import json
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives import serialization

FRIENDS_DB_PATH = "friends.json"

# internal functions
def _load_friends() -> list:
    try:
        with open(FRIENDS_DB_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    
def _save_friends(friends: list):
    with open(FRIENDS_DB_PATH, "w") as f:
        json.dump(friends, f, indent=2)
    
# api
def create_friend(user_id: str, ip:str, port: int, friend_id:str, public_key: str, profile_base64: str) -> dict:
    friends = _load_friends()

    for friend in friends:
        if friend['user_id'] == user_id and friend['friend_id'] == friend_id:
            return {
                "status": "error", 
                "message": "Friend already exists"
            }

    friends.append({
        "user_id": user_id,
        "ip": ip,
        "port": port,
        "friend_id": friend_id,
        "public_key": public_key,
        "profile_base64": profile_base64,
        "messages_list": []
    })
    _save_friends(friends)

    return {
        "status": "success", 
        "message": "Friend created successfully",
        "data": {
            "user_id": user_id,
            "ip": ip,
            "friend_id": friend_id,
            "public_key": public_key,
            "profile_base64": profile_base64,
            "messages_list": []
        }
    }

def create_message(user_id: str, friend_id: str, sender_id: str, text: str = '', latent_string: str | None = None, encrypted_seed: str = '', timestamp: float = time.time(), is_read: bool = False) -> dict:
    friends = _load_friends()

    for friend in friends:
        if  friend['user_id'] == user_id and friend['friend_id'] == friend_id:
            message = {
                "sender_id": sender_id,
                "text": text,
                "latent_string": latent_string,
                "encrypted_seed": encrypted_seed,
                "timestamp" : timestamp,
                "is_read": is_read
            }
            friend['messages_list'].append(message)
            with open(FRIENDS_DB_PATH, "w") as f:
                json.dump(friends, f, indent=2)
            return {
                "status": "success", 
                "message": "Message sent successfully",
                "sender_id": message['sender_id'],
                "text": message['text'],
                "timestamp": message['timestamp'],
                "latent_string": message['latent_string'],
                "encrypted_seed": message['encrypted_seed'],
                "is_read": message['is_read']
            }
    
    return {
        "status": "error", 
        "message": "Friend not found"
    }

def delete_friend(user_id: str, friend_id: str) -> dict:
    friends = _load_friends()

    friends = [friend for friend in friends if friend['user_id'] != user_id and friend['friend_id'] != friend_id]
    _save_friends(friends)

    return {
        "status": "success", 
        "message": "Friend deleted successfully"
    }

def get_friends(user_id: str) -> dict:
    friends = _load_friends()

    user_friends = [friend for friend in friends if friend['user_id'] == user_id]

    return {
        "status": "success", 
        "message": "Friends retrieved successfully",
        "data": {
            "friends": user_friends
        }
    }

def update_friend_profile(user_id:str, friend_id: str, profile_base64: str | None) -> dict:
    friends = _load_friends()

    for friend in friends:
        if friend["user_id"] == user_id and friend['friend_id'] == friend_id:
            friend['profile_base64'] = profile_base64
            _save_friends(friends)
            return {
                "status": "success", 
                "message": "Friend profile updated successfully",
                "data": {
                    "user_id": user_id,
                    "friend_id": friend_id,
                    "profile_base64": profile_base64
                }
            }
    
    return {
        "status": "error",
        "message": "Friend not found"
    }
