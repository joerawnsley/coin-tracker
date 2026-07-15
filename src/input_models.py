from pydantic import BaseModel

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