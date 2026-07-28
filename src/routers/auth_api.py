from fastapi import APIRouter, Form, status
from fastapi.responses import RedirectResponse

from src.auth import get_user, hash_password, user_db

router = APIRouter()


@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    user_data = get_user(user_db, username)
    if not user_data:
        return RedirectResponse(
            url="/login?error=Invalid credentials", 
            status_code=status.HTTP_303_SEE_OTHER
        )

    hashed_password = hash_password(password)
    if hashed_password != user_data.hashed_password:
        return RedirectResponse(
            url="/login?error=Invalid credentials", 
            status_code=status.HTTP_303_SEE_OTHER
        )

    response = RedirectResponse(
        url="/coins", 
        status_code=status.HTTP_303_SEE_OTHER
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {user_data.username}",
        httponly=True,
        max_age=1800
    )

    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response