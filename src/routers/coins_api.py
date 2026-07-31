from fastapi import APIRouter, Cookie, Header, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from src.database_models import Coin, Duty
from src.input_models import NewCoin, NewDuty, DutyUpdate
from src.utils import coin_to_dict, duty_to_dict
from src.auth import User, get_user, get_current_user, hash_password, user_db
from typing import Annotated

router = APIRouter()
security = HTTPBasic()

def authenticate_api_call(username, password, db):
    user_data = get_user(db, username)
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

# -----welcome endpoint-----
@router.get("/api", response_class=JSONResponse)
def root():
    return {"message": "Welcome to the Coins API"}

# -----coin routes-----

@router.get("/api/coins", response_class=JSONResponse)
def list_coins():
    query = Coin.select()
    coin_list = []
    for coin in query:
        coin_list.append(coin_to_dict(coin))
    return coin_list

@router.post("/api/coins", status_code=201, response_class=JSONResponse)
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
    

@router.get("/api/coins/{coin_path}", response_class=JSONResponse)
def single_coin(coin_path):
    selected_coin = Coin.get(Coin.coin_path == coin_path)
    return coin_to_dict(selected_coin)

@router.delete("/api/coins/{coin_path}")
def delete_coin(coin_path):
    Coin.delete().where(Coin.coin_path == coin_path).execute()
    return "Coin deleted"

# for adding and removing duties from coins
@router.put("/api/coins/{coin_path}/add-duties", response_class=JSONResponse)
def add_duties_to_coin(coin_path, duties: list[int]):
    selected_coin = Coin.get(Coin.coin_path == coin_path)
    for number in duties:
        selected_coin.duties.add(Duty.get(Duty.duty_number == number))
    return coin_to_dict(selected_coin)


@router.put("/api/coins/{coin_path}/remove-duties", response_class=JSONResponse)
def remove_duties_from_coin(coin_path, duties: list[int]):
    selected_coin = Coin.get(Coin.coin_path == coin_path)
    for number in duties:
        selected_coin.duties.remove(Duty.get(Duty.duty_number == number))
    return coin_to_dict(selected_coin)

@router.put("/api/coins/{coin_path}/mark-complete", response_class=JSONResponse)
def mark_coin_complete(
        coin_path: str, 
        access_token: str | None = None, 
        credentials: Annotated[HTTPBasicCredentials | None, Depends(security)] = None
    ):
    
    if access_token:
        get_current_user(access_token)
    else:
        authenticate_api_call(credentials.username, credentials.password, user_db)
        
    Coin.update({Coin.is_complete: True}).where(Coin.coin_path == coin_path).execute()
    updated_coin = Coin.get(Coin.coin_path == coin_path)
    return coin_to_dict(updated_coin)

@router.put("/api/coins/{coin_path}/mark-incomplete", response_class=JSONResponse)
def mark_coin_incomplete(coin_path):
    Coin.update({Coin.is_complete: False}).where(Coin.coin_path == coin_path).execute()
    updated_coin = Coin.get(Coin.coin_path == coin_path)
    return coin_to_dict(updated_coin)

@router.get("/api/coins/{coin_path}/list-duties", response_class=JSONResponse)
def list_coin_duties(coin_path):
    selected_coin = Coin.get(Coin.coin_path == coin_path)
    duties_list = []
    for duty in selected_coin.duties:
        duties_list.append(duty_to_dict(duty))
    return duties_list

# -----duties routes-----

@router.get("/api/duties", response_class=JSONResponse)
def list_duties():
    query = Duty.select()
    duty_list = []
    for duty in query:
        duty_list.append(duty_to_dict(duty))
    return duty_list

@router.get("/api/duties/{duty_number}", response_class=JSONResponse)
def single_duty(duty_number):
    selected_duty = Duty.get(Duty.duty_number == duty_number)
    return duty_to_dict(selected_duty)

@router.post("/api/duties", status_code=201, response_class=JSONResponse)
def add_duty(duty: NewDuty):
    Duty.create(
        duty_number = duty.duty_number,
        description = duty.description
    )
    created_duty = Duty.get(Duty.duty_number == duty.duty_number)
    return duty_to_dict(created_duty)

@router.put("/api/duties/{duty_number}/update", response_class=JSONResponse)
def update_duty_description(duty_number, update: DutyUpdate):
    selected_duty = Duty.get(Duty.duty_number == duty_number)
    if update.duty_number != selected_duty.duty_number and update.duty_number is not None:
        return "Error: cannot change duty numbers"
    
    selected_duty.description = update.description
    selected_duty.save(only=[Duty.description])
    return selected_duty

@router.delete("/api/duties/{duty_number}", response_class=PlainTextResponse)
def delete_duty():
    return "Error: Duties are forever. They cannot be deleted."
