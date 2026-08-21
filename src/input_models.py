import re
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

# #validation for the input data models
''' 
to do: 
- check error messages
- handle 422 error in the frontend
'''

def no_special_characters(value: str) -> str:
        if not re.match(r"^[a-zA-Z0-9 ]+$", value):
            raise ValueError('must not contain special characters')

        # replace multiple spaces with a single space and strip leading/trailing spaces
        return re.sub(r" {2,}", " ", value).strip()

def alphanumeric_and_hyphens_only(value: str) -> str:
        if not re.match(r"^[a-zA-Z0-9\-]+$", value):
            raise ValueError('letters, numbers and hyphens only')

        return value.lower()

def alphanumeric_with_basic_punctuation(value: str) -> str:
        if not re.match(r"^[A-Za-z0-9\s.,!?\'\"\-\/\(\)]+$", value):
            raise ValueError('Only letters, numbers and basic punctuation (. , ! ? \' \" -) allowed')

        return value

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
    description: Annotated[
        str,
        Field(min_length=1, max_length=250),
        BeforeValidator(alphanumeric_with_basic_punctuation)
    ]


class DutyUpdate(BaseModel):
    duty_number: int | None = None
    description: Annotated[
        str,
        Field(min_length=1, max_length=250),
        BeforeValidator(alphanumeric_with_basic_punctuation)
    ]
