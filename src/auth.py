import os

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from fastapi import HTTPException, status

from src.database_models import User

ph = PasswordHasher()

def get_user_dict_from_db():
    query = User.select().order_by(User.username)
    user_dictionary = {}
    for user in query:
        user_dictionary[user.username] = {
            "username": user.username,
            "role": user.role,
            "hashed_password": user.hashed_password,
            "uuid": user.id,
        }
    return user_dictionary


user_db = get_user_dict_from_db


def get_user_from_username(username: str):
    # probably not the most efficient way to do this, but it works for now
    #refactor
    all_user_dict = user_db()
    if username in all_user_dict:
        user_dict = all_user_dict[username]
        return User(**user_dict)


# def decode_token(token: str):
#     # not yet secure
#     # placeholder for JWT base64 decoding logic
#     #JWT
#     # maybe don't need this function at all, just put all the logic in get_user_from_token
#     user = get_user_from_username(token)
#     return user


def get_user_from_token(access_token):
    #JWT
    # reads the access_token cookie and returns the user object if valid, otherwise raises an HTTPException
    # add logic here to decode the JWT token, check the signature and extract the username
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
        )
    
    decoded_token = jwt.decode(access_token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    username = decoded_token.get("sub")
    user_data = get_user_from_username(username)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization credentials",
        )
    return user_data


def authenticate_api_call(username, password):
    user_data = get_user_from_username(username)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization credentials",
        )
    try:
        ph.verify(user_data.hashed_password, password)
    except (VerificationError, VerifyMismatchError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization credentials",
        )
    return user_data
