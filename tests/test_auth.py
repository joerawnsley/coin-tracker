import os
from http.cookies import SimpleCookie
from sys import exc_info

import jwt
import pytest
from argon2 import PasswordHasher
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.app import app
from src.auth import get_user_from_token, get_user_from_username
from src.database_models import User
from src.routers.coins_ui import login

ph = PasswordHasher()
client = TestClient(app)


def test_get_user_returns_correct_type(full_database):
    user_in_db = get_user_from_username("joe")
    assert isinstance(user_in_db, User)


def test_get_user_returns_correct_data(full_database):
    user_in_db = get_user_from_username("joe")
    ph.verify(user_in_db.hashed_password, "secret")
    assert user_in_db.username == "joe"
    assert user_in_db.role == "user"


def test_get_user_from_token(full_database):
    username = "joe"
    encoded_jwt = jwt.encode(
        {"sub": username}, os.getenv("JWT_SECRET"), algorithm="HS256"
    )
    user = get_user_from_token(encoded_jwt)
    assert user.username == "joe"
    assert user.role == "user"


def test_get_current_user_not_exists(full_database):
    username = "alice"
    encoded_jwt = jwt.encode(
        {"sub": username}, os.getenv("JWT_SECRET"), algorithm="HS256"
    )

    with pytest.raises(HTTPException):
        get_user_from_token(encoded_jwt)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "not authorized"

def test_login_converts_form_submission_to_token(full_database):

    # response = login(username="joe", password="secret")
    response = client.post(
        "/login",
        data={"username": "joe", "password": "secret"},
    )
    print(dict(response.cookies))
    token = response.cookies.get("access_token")
    # set_cookie_header = response.headers.get("set-cookie")
    # print(set_cookie_header)
    # cookie = SimpleCookie()
    # cookie.load(set_cookie_header)
    # token = cookie["access_token"].value

    response_cookie_header = jwt.decode(
        token,
        os.getenv("JWT_SECRET"),
        algorithms=["HS256"],
    )

    assert response.status_code == 303
    assert response_cookie_header.get("sub") == "joe"
