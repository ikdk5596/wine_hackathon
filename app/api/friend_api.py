import os
import time
import json
import numpy as np

FRIENDS_DB_PATH = "db/friends.json"
LATENTS_DB_PATH = "db/latents/"

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

def _get_latent_path(user_id: str, friend_id: str, enc_seed_string: str) -> str:
    save_dir = os.path.join(LATENTS_DB_PATH, user_id, friend_id)
    os.makedirs(save_dir, exist_ok=True)

    filename = f"{enc_seed_string[:10]}.npy"
    full_path = os.path.join(save_dir, filename)
    
    return save_dir, full_path
    
# api
def create_friend(user_id: str, ip:str, port: int, friend_id:str, public_key: str, profile_base64: str, double_ratchet_info) -> dict:
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
        "messages_list": [],
        "double_ratchet_info" : double_ratchet_info
    })
    _save_friends(friends)

    return {
        "status": "success", 
        "message": "Friend created successfully",
        "data": {
            "user_id": user_id,
            "ip": ip,
            "port": port,
            "friend_id": friend_id,
            "public_key": public_key,
            "profile_base64": profile_base64,
            "messages_list": [],
            "double_ratchet_info": double_ratchet_info
        }
    }

def create_text_message(user_id: str, friend_id: str, sender_id: str, text: str, double_ratchet_info: dict,
                   timestamp: float = time.time(), is_read: bool = False) -> dict:
    friends = _load_friends()

    for friend in friends:
        if  friend['user_id'] == user_id and friend['friend_id'] == friend_id:
            message = {
                "sender_id": sender_id,
                "text": text,
                "timestamp" : timestamp,
                "is_read": is_read
            }
            friend['messages_list'].append(message)
            friend['double_ratchet_info'] = double_ratchet_info
            _save_friends(friends)

            return {
                "status": "success", 
                "message": "Message sent successfully",
                "data": {
                    "sender_id": sender_id,
                    "text": text,
                    "timestamp" : timestamp,
                    "is_read": is_read
                }
            }
    
    return {
        "status": "error", 
        "message": "Friend not found"
    }

def create_latent_message(user_id: str, friend_id: str, sender_id: str, enc_latent_size: int,
                   enc_latent_array: np.ndarray, enc_seed_string: str, seed_string: str,
                   timestamp: float = time.time(), is_read: bool = False) -> dict:
    friends = _load_friends()

    for friend in friends:
        if  friend['user_id'] == user_id and friend['friend_id'] == friend_id:
            save_dir, enc_latent_path = _get_latent_path(user_id, friend_id, enc_seed_string)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            np.save(enc_latent_path, enc_latent_array)

            message = {
                "sender_id": sender_id,
                "enc_latent_size": enc_latent_size,
                "enc_latent_path": enc_latent_path,
                "enc_seed_string": enc_seed_string,
                "seed_string": seed_string,
                "timestamp" : timestamp,
                "is_read": is_read
            }

            friend['messages_list'].append(message)
            _save_friends(friends)

            return {
                "status": "success", 
                "message": "Message sent successfully",
                "data": {
                    "sender_id": sender_id,
                    "enc_latent_size": enc_latent_size,
                    "enc_latent_array": enc_latent_array,
                    "enc_seed_string": enc_seed_string,
                    "seed_string": seed_string,
                    "timestamp" : timestamp,
                    "is_read": is_read
                }
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

    for friend in user_friends:
        for message in friend['messages_list']:
            if 'enc_latent_path' in message:
                enc_latent_path = message['enc_latent_path']
                if os.path.exists(enc_latent_path):
                    message['enc_latent_array'] = np.load(enc_latent_path)
                else:
                    message['enc_latent_array'] = None
    
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

def read_messages(user_id: str, friend_id: str) -> dict:
    friends = _load_friends()

    for friend in friends:
        if friend['user_id'] == user_id and friend['friend_id'] == friend_id:
            for message in friend['messages_list'][::-1]:
                if not message['is_read']:
                    message['is_read'] = True
                else:
                    break
            _save_friends(friends)
            return {
                "status": "success",
                "message": "Messages marked as read",
            }
    
    return {
        "status": "error",
        "message": "Friend not found"
    }