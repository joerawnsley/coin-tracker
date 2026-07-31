from fastapi import Cookie, HTTPException, status
from pydantic import BaseModel

fake_users_db = {
    "joe": {
        "username": "joe",
        "hashed_password": "fakehashedsecret"
    },
    "admin": {
        "username": "admin",
        "hashed_password": "fakehashedadmin"
    },
    "testuser": {
            "username": "testuser",
            "hashed_password": "fakehashed12345678"
        }
}

user_db = fake_users_db


class User(BaseModel):
    username: str
    email: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str
    
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    
    
def hash_password(password: str):
    # not yet secure
    return "fakehashed" + password

def decode_token(token: str):
    # not yet secure
    user = get_user(user_db, token)
    return user


def get_current_user(access_token):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = access_token.replace("Bearer ", "") if access_token.startswith("Bearer ") else access_token

    user = decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user

def authenticate_api_call(username, password, db):
    user_data = get_user(db, username)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    hashed_password = hash_password(password)
    if hashed_password != user_data.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

# is this used? delete if not
def get_current_username(access_token: str | None = Cookie(default=None)):
    if not access_token:
        return None
    
    token = access_token.replace("Bearer ", "") if access_token.startswith("Bearer ") else access_token

    user = decode_token(token)
    if not user:
        return None
    return user.username