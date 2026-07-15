from fastapi import Request, Form, status
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from src.input_models import NewCoin, NewDuty, DutyUpdate
from fastapi.templating import Jinja2Templates
from typing import Annotated
from src.app import app
import src.coins_api as coins_api


templates = Jinja2Templates(directory="src/templates")

@app.get("/", response_class=HTMLResponse)
def welcome_page(request: Request):
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
            "subpages": subpages
        }
    )

@app.get("/coins", response_class=HTMLResponse)
def coins_list_page(request: Request):
    coins = coins_api.list_coins()
    return templates.TemplateResponse(
        request=request,
        name="coins.html",
        context={
            "coins": coins
        }
    )

@app.get("/duties", response_class=HTMLResponse)
def duties_list_page(request: Request):
    duties = coins_api.list_duties()
    return templates.TemplateResponse(
        request=request,
        name="duties.html",
        context={
            "duties": duties,
            "page_mode": "all"
        }
    )

@app.get("/duties/{duty_number}", response_class=HTMLResponse)
def single_duty_page(duty_number: int, request: Request):
    duties = [coins_api.single_duty(duty_number)]
    return templates.TemplateResponse(
        request=request,
        name="duties.html",
        context={
            "duties": duties,
            "page_mode": "single"
        }
    )

@app.get("/edit-coin/{coin_path}", response_class=HTMLResponse)
def edit_coin_page(request: Request, coin_path: str):
    selected_coin = coins_api.single_coin(coin_path)
    all_duties = coins_api.list_duties()
    return templates.TemplateResponse(
        request=request,
        name="edit-coin.html",
        context={
            "coin": selected_coin,
            "duties": all_duties
        }
    )

@app.post("/edit-coin/{coin_path}")
def edit_coin_submit(
        request: Request, 
        coin_path: str,
        duties: Annotated[list[int], Form()] = [],
        completed: Annotated[bool, Form()] = False
    ):
    original_coin = coins_api.single_coin(coin_path)
    original_duties = original_coin["duties"]
    original_status = original_coin["isComplete"]
    
    coins_api.remove_duty_from_coin(coin_path, original_duties)
    coins_api.add_duty_to_coin(coin_path, duties)
    
    if completed and not original_status:
        coins_api.mark_coin_complete(coin_path)
    if original_status and not completed:
        coins_api.mark_coin_incomplete(coin_path)
    
    return RedirectResponse(
            url="/coins",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
@app.get("/create-coin", response_class=HTMLResponse)
def create_coin_page(request: Request):
    all_duties = coins_api.list_duties()
    return templates.TemplateResponse(
        request=request,
        name="create-coin.html",
        context={
            "duties": all_duties
        }
    )

@app.post("/create-coin")
def create_coin_submit(
        coin_path: str = Form(),
        coin_name: str = Form(),
        duties: Annotated[list[int], Form()] = [],
    ):
    new_coin = NewCoin(
        coin_name=coin_name,
        coin_path=coin_path,
        duties=duties
    )
    
    coins_api.add_coin(new_coin)
    
    return RedirectResponse(
            url="/coins",
            status_code=status.HTTP_303_SEE_OTHER
        )