import re
from typing import Self

from pydantic import BaseModel, Field, model_validator

# #validation for the input data models
''' 
to do: 
- allow spaces in coin_name
- change error message
- handle 422 error in the frontend
- test and build out validation on other input models
'''
name_pattern = r"^[a-zA-Z0-9 ]+$"

class NewCoin(BaseModel):
    coin_name: str = Field(
        min_length=1, 
        max_length=50)
    coin_path: str
    duties: list[int] | None = None
    is_complete: bool | None = None

    @model_validator(mode='after')
    def verify_coin_name(self) -> Self:
        if not re.match(name_pattern, self.coin_name):
            raise ValueError('coin name must not contain special characters')
        if re.search(r" {2,}", self.coin_name):
            self.coin_name = re.sub(r" {2,}", " ", self.coin_name)
        return self



class NewDuty(BaseModel):
    duty_number: int
    description: str


class DutyUpdate(BaseModel):
    duty_number: int | None = None
    description: str
