from fastapi import Cookie, HTTPException, status

from src.database_models import User


def fake_users_db():
    return {
        "joe": {
            "username": "joe",
            "hashed_password": "fakehashedsecret",
            "role": "user",
        },
        "admin": {
            "username": "admin",
            "hashed_password": "fakehashedadmin",
            "role": "admin",
        },
        "testuser": {
            "username": "testuser",
            "hashed_password": "fakehashed12345678",
            "role": "user",
        },
    }


def get_user_dict_from_db():
    query = User.select().order_by(User.username)
    user_dictionary = {}
    for user in query:
        user_dictionary[user.username] = {
            "username": user.username,
            "role": user.role,
            "hashed_password": user.hashed_password,
        }
    return user_dictionary


user_db = get_user_dict_from_db


def get_user_from_username(username: str):
    all_user_dict = user_db()
    if username in all_user_dict:
        user_dict = all_user_dict[username]
        return User(**user_dict)


def hash_password(password: str):
    # not yet secure
    return "fakehashed" + password


def decode_token(token: str):
    # not yet secure
    user = get_user_from_username(token)
    return user


def get_user_from_token(access_token):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    token = (
        access_token.replace("Bearer ", "")
        if access_token.startswith("Bearer ")
        else access_token
    )
    user = decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user


def authenticate_api_call(username, password):
    user_data = get_user_from_username(username)
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
    return user_data


# is this used? delete if not
def get_current_username(access_token: str | None = Cookie(default=None)):
    if not access_token:
        return None

    token = (
        access_token.replace("Bearer ", "")
        if access_token.startswith("Bearer ")
        else access_token
    )

    user = decode_token(token)
    if not user:
        return None
    return user.username
