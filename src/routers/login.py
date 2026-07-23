from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from src.auth import user_db, get_user, hash_password

router = APIRouter()

@router.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_data = get_user(user_db, form_data.username)
    # user_dict = user_db.get(form_data.username)
    if not user_data:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    hashed_password = hash_password(form_data.password)
    if hashed_password != user_data.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Return the username as the token (for now)
    return {"access_token": user_data.username, "token_type": "bearer"}
