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
    # note: this will work well for authenticating API calls, but prevents pages from loading if not logged in
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

def get_current_username(access_token: str | None = Cookie(default=None)):
    if not access_token:
        return None
    
    token = access_token.replace("Bearer ", "") if access_token.startswith("Bearer ") else access_token

    user = decode_token(token)
    if not user:
        return None
    return user.username