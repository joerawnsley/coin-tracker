from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

def decode_token(token):
    # not yet secure
    user = get_user(user_db, token)
    return user

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user