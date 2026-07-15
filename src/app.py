from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from src.models import Coin, Duty
from src.database import db
from src.utils import coin_to_dict, duty_to_dict
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from typing import Annotated

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")

# -----welcome endpoint-----
@app.get("/api", response_class=JSONResponse)
def root():
    return {"message": "Welcome to the Coins API"}

# ---- input models ---

class NewCoin(BaseModel):
    coin_name: str
    coin_path: str
    duties: list[int] | None = None
    is_complete: bool | None = None

class NewDuty(BaseModel):
    duty_number: int
    description: str

class DutyUpdate(BaseModel):
    duty_number: int | None = None
    description: str

# -----coin routes-----

@app.get("/api/coins", response_class=JSONResponse)
def list_coins():
    query = Coin.select()
    coin_list = []
    for coin in query:
        coin_list.append(coin_to_dict(coin))
    return coin_list

@app.post("/api/coins", status_code=201, response_class=JSONResponse)
def add_coin(coin: NewCoin):
    Coin.create(
        coin_name=coin.coin_name,
        coin_path=coin.coin_path
    )
    if coin.duties:
        saved_coin = Coin.get(Coin.coin_name == coin.coin_name)
        for number in coin.duties:
            saved_coin.duties.add(Duty.get(Duty.duty_number == int(number)))
    
    created_coin = Coin.get(Coin.coin_path == coin.coin_path)
    return coin_to_dict(created_coin)
    

@app.get("/api/coins/{coin_path}", response_class=JSONResponse)
def single_coin(coin_path):
    selected_coin = Coin.get(Coin.coin_path == coin_path)
    return coin_to_dict(selected_coin)

@app.delete("/api/coins/{coin_path}")
def delete_coin(coin_path):
    Coin.delete().where(Coin.coin_path == coin_path).execute()
    return "Coin deleted"

# for adding and removing duties from coins
@app.put("/api/coins/{coin_path}/add-duties", response_class=JSONResponse)
def add_duty_to_coin(coin_path, duties: list[int]):
    selected_coin = Coin.get(Coin.coin_path == coin_path)
    for number in duties:
        selected_coin.duties.add(Duty.get(Duty.duty_number == number))
    return coin_to_dict(selected_coin)


@app.put("/api/coins/{coin_path}/remove-duties", response_class=JSONResponse)
def remove_duty_from_coin(coin_path, duties: list[int]):
    selected_coin = Coin.get(Coin.coin_path == coin_path)
    for number in duties:
        selected_coin.duties.remove(Duty.get(Duty.duty_number == number))
    return coin_to_dict(selected_coin)

@app.put("/api/coins/{coin_path}/mark-complete", response_class=JSONResponse)
def mark_coin_complete(coin_path):
    Coin.update({Coin.is_complete: True}).where(Coin.coin_path == coin_path).execute()
    updated_coin = Coin.get(Coin.coin_path == coin_path)
    return coin_to_dict(updated_coin)

@app.put("/api/coins/{coin_path}/mark-incomplete", response_class=JSONResponse)
def mark_coin_incomplete(coin_path):
    Coin.update({Coin.is_complete: False}).where(Coin.coin_path == coin_path).execute()
    updated_coin = Coin.get(Coin.coin_path == coin_path)
    return coin_to_dict(updated_coin)

@app.get("/api/coins/{coin_path}/list-duties", response_class=JSONResponse)
def list_coin_duties(coin_path):
    selected_coin = Coin.get(Coin.coin_path == coin_path)
    duties_list = []
    for duty in selected_coin.duties:
        duties_list.append(duty_to_dict(duty))
    return duties_list

# -----duties routes-----

@app.get("/api/duties", response_class=JSONResponse)
def list_duties():
    query = Duty.select()
    duty_list = []
    for duty in query:
        duty_list.append(duty_to_dict(duty))
    return duty_list

@app.get("/api/duties/{duty_number}", response_class=JSONResponse)
def single_duty(duty_number):
    selected_duty = Duty.get(Duty.duty_number == duty_number)
    return duty_to_dict(selected_duty)

@app.post("/api/duties", status_code=201, response_class=JSONResponse)
def add_duty(duty: NewDuty):
    Duty.create(
        duty_number = duty.duty_number,
        description = duty.description
    )
    created_duty = Duty.get(Duty.duty_number == duty.duty_number)
    return duty_to_dict(created_duty)

@app.put("/api/duties/{duty_number}/update", response_class=JSONResponse)
def update_duty_description(duty_number, update: DutyUpdate):
    selected_duty = Duty.get(Duty.duty_number == duty_number)
    if update.duty_number != selected_duty.duty_number and update.duty_number is not None:
        return "Error: cannot change duty numbers"
    
    selected_duty.description = update.description
    selected_duty.save(only=[Duty.description])
    return selected_duty

@app.delete("/api/duties/{duty_number}", response_class=PlainTextResponse)
def delete_duty():
    return "Error: Duties are forever. They cannot be deleted."


# ------- FRONT END ---------

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
    coins = list_coins()
    return templates.TemplateResponse(
        request=request,
        name="coins.html",
        context={
            "coins": coins
        }
    )

@app.get("/duties", response_class=HTMLResponse)
def duties_list_page(request: Request):
    duties = list_duties()
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
    duties = [single_duty(duty_number)]
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
    selected_coin = single_coin(coin_path)
    all_duties = list_duties()
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
    original_coin = single_coin(coin_path)
    original_duties = original_coin["duties"]
    original_status = original_coin["isComplete"]
    
    remove_duty_from_coin(coin_path, original_duties)
    add_duty_to_coin(coin_path, duties)
    
    if completed and not original_status:
        mark_coin_complete(coin_path)
    if original_status and not completed:
        mark_coin_incomplete(coin_path)
    
    return RedirectResponse(
            url="/coins",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
@app.get("/create-coin", response_class=HTMLResponse)
def create_coin_page(request: Request):
    all_duties = list_duties()
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
    
    add_coin(new_coin)
    
    return RedirectResponse(
            url="/coins",
            status_code=status.HTTP_303_SEE_OTHER
        )