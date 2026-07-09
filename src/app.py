from fastapi import FastAPI
from src.models import Coin, Duty
from src.database import db
from src.utils import coin_to_dict, duty_to_dict
from pydantic import BaseModel

app = FastAPI()

# -----welcome endpoint-----
@app.get("/api")
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

@app.get("/api/coins")
def list_coins():
    query = Coin.select()
    coin_list = []
    for coin in query:
        coin_list.append(coin_to_dict(coin))
    return coin_list

@app.post("/api/coins", status_code=201)
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
    

@app.get("/api/coins/{coin_path}")
def single_coin(coin_path):
    selected_coin = Coin.get(Coin.coin_path == coin_path)
    return coin_to_dict(selected_coin)

@app.delete("/api/coins/{coin_path}")
def delete_coin(coin_path):
    Coin.delete().where(Coin.coin_path == coin_path).execute()
    return "Coin deleted"

# for adding and removing duties from coins
@app.put("/api/coins/{coin_path}/add-duties")
def add_duty_to_coin(coin_path, duties: list[int]):
    selected_coin = Coin.get(Coin.coin_path == coin_path)
    for number in duties:
        selected_coin.duties.add(Duty.get(Duty.duty_number == number))
    return coin_to_dict(selected_coin)


@app.put("/api/coins/{coin_path}/remove-duties")
def remove_duty_from_coin(coin_path, duties: list[int]):
    selected_coin = Coin.get(Coin.coin_path == coin_path)
    for number in duties:
        selected_coin.duties.remove(Duty.get(Duty.duty_number == number))
    return coin_to_dict(selected_coin)

@app.put("/api/coins/{coin_path}/mark-complete")
def mark_coin_complete(coin_path):
    selected_coin = Coin.get(Coin.coin_path == coin_path)
    selected_coin.update(is_complete=True).execute()
    updated_coin = Coin.get(Coin.coin_path == coin_path)
    return coin_to_dict(updated_coin)

@app.put("/api/coins/{coin_path}/mark-incomplete")
def mark_coin_incomplete(coin_path):
    selected_coin = Coin.get(Coin.coin_path == coin_path)
    selected_coin.update(is_complete=False).execute()
    updated_coin = Coin.get(Coin.coin_path == coin_path)
    return coin_to_dict(updated_coin)

@app.get("/api/coins/{coin_path}/list-duties")
def list_coin_duties(coin_path):
    selected_coin = Coin.get(Coin.coin_path == coin_path)
    duties_list = []
    for duty in selected_coin.duties:
        duties_list.append(duty_to_dict(duty))
    print(duties_list)
    return duties_list

# -----duties routes-----

@app.get("/api/duties")
def list_duties():
    print("hello from listduties")
    query = Duty.select()
    duty_list = []
    for duty in query:
        duty_list.append(duty_to_dict(duty))
    return duty_list

@app.get("/api/duties/{duty_number}")
def single_duty(duty_number):
    selected_duty = Duty.get(Duty.duty_number == duty_number)
    return duty_to_dict(selected_duty)

@app.post("/api/duties", status_code=201)
def add_duty(duty: NewDuty):
    Duty.create(
        duty_number = duty.duty_number,
        description = duty.description
    )
    created_duty = Duty.get(Duty.duty_number == duty.duty_number)
    return duty_to_dict(created_duty)

@app.put("/api/duties/{duty_number}/update")
def update_duty_description(duty_number, update: DutyUpdate):
    selected_duty = Duty.get(Duty.duty_number == duty_number)
    if update.duty_number != selected_duty.duty_number and update.duty_number is not None:
        return "Error: cannot change duty numbers"
    
    selected_duty.description = update.description
    selected_duty.save(only=[Duty.description])
    return selected_duty

@app.delete("/api/duties/{duty_number}")
def delete_duty():
    return "Error: Duties are forever. They cannot be deleted."
