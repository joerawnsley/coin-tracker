from fastapi import APIRouter, Request, Form, status, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from src.input_models import NewCoin, NewDuty, DutyUpdate
from fastapi.templating import Jinja2Templates
from typing import Annotated
import src.routers.coins_api as coins_api

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/", response_class=HTMLResponse)
def welcome_page(request: Request, access_token: Annotated[str | None, Cookie()] = None):
    subpages = [
        {"title": "All Coins",
         "endpoint": "coins_list_page"
        },
        {"title": "All Duties",
         "endpoint": "duties_list_page"
        }
    ]
    return templates.TemplateResponse(
        request=request,
        name="welcome.html",
        context={
            "subpages": subpages,
            "access_token": access_token
        }
    )

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, access_token: Annotated[str | None, Cookie()] = None):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "access_token": access_token
        }
    )

@router.get("/coins", response_class=HTMLResponse)
def coins_list_page(request: Request, access_token: Annotated[str | None, Cookie()] = None):
    coins = coins_api.list_coins()
    return templates.TemplateResponse(
        request=request,
        name="coins.html",
        context={
            "coins": coins,
            "access_token": access_token
        }
    )

@router.get("/duties", response_class=HTMLResponse)
def duties_list_page(request: Request, access_token: Annotated[str | None, Cookie()] = None):
    duties = coins_api.list_duties()
    return templates.TemplateResponse(
        request=request,
        name="duties.html",
        context={
            "duties": duties,
            "page_mode": "all",
            "access_token": access_token
        }
    )

@router.get("/duties/{duty_number}", response_class=HTMLResponse)
def single_duty_page(duty_number: int, request: Request, access_token: Annotated[str | None, Cookie()] = None):
    duties = [coins_api.single_duty(duty_number)]
    return templates.TemplateResponse(
        request=request,
        name="duties.html",
        context={
            "duties": duties,
            "page_mode": "single",
            "access_token": access_token
        }
    )

@router.get("/edit-coin/{coin_path}", response_class=HTMLResponse)
def edit_coin_page(request: Request, coin_path: str, access_token: Annotated[str | None, Cookie()] = None):
    selected_coin = coins_api.single_coin(coin_path)
    all_duties = coins_api.list_duties()
    return templates.TemplateResponse(
        request=request,
        name="edit-coin.html",
        context={
            "coin": selected_coin,
            "duties": all_duties,
            "access_token": access_token
        }
    )

@router.post("/edit-coin/{coin_path}")
def edit_coin_submit(
        request: Request, 
        coin_path: str,
        duties: Annotated[list[int], Form()] = [],
        completed: Annotated[bool, Form()] = False, 
        access_token: Annotated[str | None, Cookie()] = None
    ):
    original_coin = coins_api.single_coin(coin_path)
    original_duties = original_coin["duties"]
    original_status = original_coin["isComplete"]
    
    coins_api.remove_duties_from_coin(coin_path, original_duties)
    coins_api.add_duties_to_coin(coin_path, duties)
    
    if completed and not original_status:
        coins_api.mark_coin_complete(coin_path)
    if original_status and not completed:
        coins_api.mark_coin_incomplete(coin_path)
    
    return RedirectResponse(
            url="/coins",
            status_code=status.HTTP_303_SEE_OTHER,
            context={
                "access_token": access_token
            }
        )
    
@router.get("/create-coin", response_class=HTMLResponse)
def create_coin_page(request: Request, access_token: Annotated[str | None, Cookie()] = None):
    all_duties = coins_api.list_duties()
    return templates.TemplateResponse(
        request=request,
        name="create-coin.html",
        context={
            "duties": all_duties,
            "access_token": access_token
        }
    )

@router.post("/create-coin")
def create_coin_submit(
        coin_path: str = Form(),
        coin_name: str = Form(),
        duties: Annotated[list[int], Form()] = [],
        access_token: Annotated[str | None, Cookie()] = None
    ):
    new_coin = NewCoin(
        coin_name=coin_name,
        coin_path=coin_path,
        duties=duties
    )
    coins_api.add_coin(new_coin)
    return RedirectResponse(
            url="/coins",
            status_code=status.HTTP_303_SEE_OTHER,
            context={
                "access_token": access_token
            }
        )

@router.post("/delete-coin/{coin_path}")
def delete_coin_submit(coin_path: str, access_token: Annotated[str | None, Cookie()] = None):
    coin_to_delete = coins_api.single_coin(coin_path)
    existing_duties = coin_to_delete["duties"]
    coins_api.remove_duties_from_coin(coin_path, existing_duties)
    
    coins_api.delete_coin(coin_path)
    
    return RedirectResponse(
            url="/coins",
            status_code=status.HTTP_303_SEE_OTHER,
            context={
                "access_token": access_token
            }
        )