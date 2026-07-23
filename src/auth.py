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

db = fake_users_db


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
    
    
def fake_hash_password(password: str):
    return "fakehashed" + password

def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    # user = fake_decode_token(token)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Not authenticated",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    # return user
    pass