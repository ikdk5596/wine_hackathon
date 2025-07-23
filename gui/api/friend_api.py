import json
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives import serialization

FRIENDS_DB_PATH = "friends.json"

def _load_friends() -> list:
    try:
        with open(FRIENDS_DB_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    
def create_friend(user_id: str, ip:str, friend_id:str, public_key: RSAPublicKey, profile_base64: str) -> dict:
    friends = _load_friends()

    for friend in friends:
        if friend['user_id'] == user_id and friend['friend_id'] == friend_id:
            return {
                "status": "error", 
                "message": "Friend already exists"
            }
        
    public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    friends.append({
        "user_id": user_id,
        "ip": ip,
        "friend_id": friend_id,
        "public_key": public_key,
        "profile_base64": profile_base64
    })
    with open(FRIENDS_DB_PATH, "w") as f:
        json.dump(friends, f, indent=2)

    return {
        "status": "success", 
        "message": "Friend created successfully",
        "user_id": user_id,
        "ip": ip,
        "friend_id": friend_id,
        "public_key": public_key,
        "profile_base64": profile_base64
    }

def get_friends(user_id: str) -> dict:
    friends = _load_friends()
    user_friends = [friend for friend in friends if friend['user_id'] == user_id]

    return {
        "status": "success", 
        "friends": user_friends
    }

def update_friend_profile(friend_id: str, profile_base64: str | None) -> dict:
    friends = _load_friends()
    for friend in friends:
        if friend['friend_id'] == friend_id:
            friend['profile_base64'] = profile_base64
            with open(FRIENDS_DB_PATH, "w") as f:
                json.dump(friends, f, indent=2)
    return {
        "status": "success", 
        "message": "Friend profile updated successfully",
        "profile_base64": profile_base64
    }

def delete_friend(user_id: str, friend_id: str) -> dict:
    friends = _load_friends()
    friends = [friend for friend in friends if friend['user_id'] != user_id and friend['friend_id'] != friend_id]

    with open(FRIENDS_DB_PATH, "w") as f:
        json.dump(friends, f, indent=2)

    return {
        "status": "success", 
        "message": "Friend deleted successfully"
    }