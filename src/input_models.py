from pydantic import BaseModel, Field


# #validation for the input data models
''' 
to do: 
- allow spaces in coin_name
- change error message
- handle 422 error in the frontend
- test and build out validation on other input models
'''
class NewCoin(BaseModel):
    coin_name: str = Field(
        min_length=1, 
        max_length=50, 
        pattern=r"^[a-zA-Z0-9]+$")
    coin_path: str
    duties: list[int] | None = None
    is_complete: bool | None = None


class NewDuty(BaseModel):
    duty_number: int
    description: str


class DutyUpdate(BaseModel):
    duty_number: int | None = None
    description: str
