import os
from sys import exc_info

import jwt
import pytest
from argon2 import PasswordHasher
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.app import app
from src.auth import get_user_from_token, get_user_from_username
from src.database_models import User

ph = PasswordHasher()
client = TestClient(app, follow_redirects=False)


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

    response = client.post(
        "/login",
        data={"username": "joe", "password": "secret"},
    )
    assert response.status_code == 303

    token = response.cookies.get("access_token")
    assert token is not None, "access_token cookie not set in response"

    response_cookie_header = jwt.decode(
        token,
        os.getenv("JWT_SECRET"),
        algorithms=["HS256"],
    )
    assert response_cookie_header.get("sub") == "joe"
