import os
from typing import Annotated

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from fastapi import APIRouter, Cookie, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.auth import (
    get_user_from_token,
    get_user_from_username,
)
from src.input_models import NewCoin
from src.routers import coins_api

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")
ph = PasswordHasher()

# =====================================================================================
#               - - - - - - - - - - WELCOME ROUTE - - - - - - - - -
# =====================================================================================


@router.get("/", response_class=HTMLResponse)
def welcome_page(
    request: Request, access_token: Annotated[str | None, Cookie()] = None
):
    try:
        username = get_user_from_token(access_token).username
    except HTTPException:
        username = None

    subpages = [
        {"title": "All Coins", "endpoint": "coins_list_page"},
        {"title": "All Duties", "endpoint": "duties_list_page"},
    ]
    return templates.TemplateResponse(
        request=request,
        name="welcome.html",
        context={"subpages": subpages, "username": username},
    )


# =====================================================================================
#               - - - - - - - - - - LIST/DETAIL ROUTES - - - - - - - - -
# =====================================================================================


@router.get("/coins", response_class=HTMLResponse)
def coins_list_page(
    request: Request,
    access_token: Annotated[str | None, Cookie()] = None,
    error: str | None = None,
):
    try:
        username = get_user_from_token(access_token).username
    except HTTPException:
        username = None

    coins = coins_api.list_coins()
    return templates.TemplateResponse(
        request=request,
        name="coins.html",
        context={"coins": coins, "username": username, "error": error},
    )


@router.get("/duties", response_class=HTMLResponse)
def duties_list_page(
    request: Request, access_token: Annotated[str | None, Cookie()] = None
):
    try:
        username = get_user_from_token(access_token).username
    except HTTPException:
        username = None

    duties = coins_api.list_duties()
    return templates.TemplateResponse(
        request=request,
        name="duties.html",
        context={"duties": duties, "page_mode": "all", "username": username},
    )


@router.get("/duties/{duty_number}", response_class=HTMLResponse)
def single_duty_page(
    duty_number: int,
    request: Request,
    access_token: Annotated[str | None, Cookie()] = None,
):
    try:
        username = get_user_from_token(access_token).username
    except HTTPException:
        username = None

    duties = [coins_api.single_duty(duty_number)]
    return templates.TemplateResponse(
        request=request,
        name="duties.html",
        context={"duties": duties, "page_mode": "single", "username": username},
    )


# =====================================================================================
#         - - - - - - - - - - CREATE/EDIT/DELETE ROUTES - - - - - - - - -
# =====================================================================================


@router.get("/edit-coin/{coin_path}", response_class=HTMLResponse)
def edit_coin_page(
    request: Request,
    coin_path: str,
    access_token: Annotated[str | None, Cookie()] = None,
):

    try:
        user = get_user_from_token(access_token)
        selected_coin = coins_api.single_coin(coin_path)
        all_duties = coins_api.list_duties()
        return templates.TemplateResponse(
            request=request,
            name="edit-coin.html",
            context={
                "coin": selected_coin,
                "duties": all_duties,
                "username": user.username,
                "role": user.role,
            },
        )
    except HTTPException:
        return RedirectResponse(
            url="/coins?error=unauthorised", status_code=status.HTTP_303_SEE_OTHER
        )


@router.post("/edit-coin/{coin_path}")
def edit_coin_submit(
    request: Request,
    coin_path: str,
    duties: Annotated[list[int], Form()] = [],  # noqa: B006
    completed: Annotated[bool, Form()] = False,
    access_token: Annotated[str | None, Cookie()] = None,
):
    original_coin = coins_api.single_coin(coin_path)
    original_duties = original_coin["duties"]
    original_status = original_coin["isComplete"]

    role = get_user_from_token(access_token).role
    if role == "admin":
        coins_api.remove_duties_from_coin(coin_path, original_duties, access_token)
        coins_api.add_duties_to_coin(coin_path, duties, access_token)

    if completed and not original_status:
        coins_api.mark_coin_complete(coin_path, access_token)
    if original_status and not completed:
        coins_api.mark_coin_incomplete(coin_path, access_token)

    return RedirectResponse(
        url="/coins",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/create-coin", response_class=HTMLResponse)
def create_coin_page(
    request: Request, access_token: Annotated[str | None, Cookie()] = None
):
    try:
        user = get_user_from_token(access_token)
        all_duties = coins_api.list_duties()
        return templates.TemplateResponse(
            request=request,
            name="create-coin.html",
            context={"duties": all_duties, "username": user.username},
        )
    except HTTPException:
        return RedirectResponse(
            url="/coins?error=unauthorised", status_code=status.HTTP_303_SEE_OTHER
        )


@router.post("/create-coin")
def create_coin_submit(
    coin_path: str = Form(),
    coin_name: str = Form(),
    duties: Annotated[list[int], Form()] = [],  # noqa: B006
    access_token: Annotated[str | None, Cookie()] = None,
):
    new_coin = NewCoin(coin_name=coin_name, coin_path=coin_path, duties=duties)
    coins_api.add_coin(new_coin, access_token)
    return RedirectResponse(
        url="/coins",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/delete-coin/{coin_path}")
def delete_coin_submit(
    coin_path: str, access_token: Annotated[str | None, Cookie()] = None
):
    coin_to_delete = coins_api.single_coin(coin_path)
    existing_duties = coin_to_delete["duties"]
    coins_api.remove_duties_from_coin(coin_path, existing_duties, access_token)

    coins_api.delete_coin(coin_path, access_token)

    return RedirectResponse(
        url="/coins",
        status_code=status.HTTP_303_SEE_OTHER,
    )


# =====================================================================================
#                    - - - - - - - - - - LOGIN ROUTES - - - - - - - - -
# =====================================================================================


@router.get("/login", response_class=HTMLResponse)
# probably don't need to pass in the access_token here, but leaving it in for now
#refactor
def login_page(
    request: Request,
    access_token: Annotated[str | None, Cookie()] = None,
    error: str | None = None,
):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"username": get_user_from_token(access_token).username if access_token else None, "error": error},
    )


@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    user_data = get_user_from_username(username)
    if not user_data:
        return RedirectResponse(
            url="/login?error=Invalid credentials",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    try:
        ph.verify(user_data.hashed_password, password)
    except (VerificationError, VerifyMismatchError):
        return RedirectResponse(
            url="/login?error=Invalid credentials",
            status_code=status.HTTP_303_SEE_OTHER,
        )


    response = RedirectResponse(url="/coins", status_code=status.HTTP_303_SEE_OTHER)
    #JWT change secret to something stored in .env file and not hardcoded 
    encoded_jwt = jwt.encode({"sub": user_data.username}, os.getenv("JWT_SECRET"), algorithm="HS256")
    response.set_cookie(
        key="access_token",
        # this is where we pass in the JWT token. #JWT
        value=encoded_jwt,
        httponly=True,
        max_age=1800,
    )

    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response
