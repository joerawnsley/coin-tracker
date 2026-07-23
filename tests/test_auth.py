from src.auth import UserInDB, get_user, get_current_user
from fastapi import HTTPException
import pytest

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

def test_get_user_returns_correct_type():
    user_in_db = get_user(fake_users_db, "joe")
    assert isinstance(user_in_db, UserInDB)
    
def test_get_user_returns_correct_data():
    user_in_db = get_user(fake_users_db, "joe")
    assert user_in_db.hashed_password == "fakehashedsecret"
    assert user_in_db.username == "joe"
    
def test_get_current_user(mocker):
    mocker.patch("src.auth.decode_token", return_value=UserInDB(
        username="joe",
        hashed_password="fakehashedsecret"
    ))
    user = get_current_user("joe")
    assert user.username == "joe"

def test_get_current_user_not_exists(mocker):
    mocker.patch("src.auth.decode_token", return_value=UserInDB(
            username="joe",
            hashed_password="fakehashedsecret"
        ))
    with pytest.raises(HTTPException):
        user = get_current_user("alice")
        