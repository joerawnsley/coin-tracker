import re
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

# #validation for the input data models
''' 
to do: 
- check error messages
- handle 422 error in the frontend
- test and build out validation on other input models
'''
# allow only alphanumeric characters and spaces in coin_name
name_pattern = r"^[a-zA-Z0-9 ]+$"
path_pattern = r"^[a-zA-Z0-9\-]+$"

def no_special_characters(value: str) -> str:
        if not re.match(name_pattern, value):
            raise ValueError('must not contain special characters')

        # replace multiple spaces with a single space and strip leading/trailing spaces
        return re.sub(r" {2,}", " ", value).strip()

def alphanumeric_and_hyphens_only(value: str) -> str:
        if not re.match(path_pattern, value):
            raise ValueError('letters, numbers and hyphens only')

        return value.lower()

class NewCoin(BaseModel):
    coin_name: Annotated[
        str, 
        Field(min_length=1, max_length=50), 
        BeforeValidator(no_special_characters)
        ]
    coin_path: Annotated[
        str,
        Field(min_length=1, max_length=100),
        BeforeValidator(alphanumeric_and_hyphens_only)
    ]
    duties: list[int] | None = None
    is_complete: bool | None = None


class NewDuty(BaseModel):
    duty_number: int
    description: str


class DutyUpdate(BaseModel):
    duty_number: int | None = None
    description: str
