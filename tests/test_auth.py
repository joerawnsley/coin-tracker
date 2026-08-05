from src.auth import get_user_from_username, get_user_from_token, user_db
from src.database_models import User
from src.routers.coins_ui import login
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import pytest


def test_get_user_returns_correct_type(full_database):
    user_in_db = get_user_from_username(user_db, "joe")
    assert isinstance(user_in_db, User)
    
def test_get_user_returns_correct_data(full_database):
    user_in_db = get_user_from_username(user_db, "joe")
    assert user_in_db.hashed_password == "fakehashedsecret"
    assert user_in_db.username == "joe"
    
def test_get_user_from_token(mocker):
    mocker.patch("src.auth.decode_token", return_value=User(
        username="joe",
        hashed_password="fakehashedsecret",
        role="user"
    ))
    user = get_user_from_token("joe")
    assert user.username == "joe"

def test_get_current_user_not_exists(mocker):
    mocker.patch("src.auth.decode_token", return_value=None)
    
    with pytest.raises(HTTPException):
        get_user_from_token("alice")

def test_login_converts_form_submission_to_token(full_database):
    response = login(username="joe", password='secret')
    set_cookie_header = response.headers.get("set-cookie")
    assert response.status_code == 303
    assert "access_token=" in set_cookie_header
    assert "Bearer joe" in set_cookie_header
    
