import uuid

from src.database_models import UserRequest


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def coin_to_dict(coin):
    return {
        "id": coin.id,
        "coinName": coin.coin_name,
        "coinPath": coin.coin_path,
        "duties": {duty.duty_number for duty in coin.duties},
        "isComplete": coin.is_complete,
    }


def duty_to_dict(duty):
    return {
        "id": duty.id,
        "dutyNumber": duty.duty_number,
        "description": duty.description,
        "coins": {coin.coin_name for coin in duty.coins},
    }

def log_request(username: str, method: str, endpoint: str, body: str, status: str = "unknown"):

    UserRequest.create(
        username=username,
        method=method,
        endpoint=endpoint,
        body=body,
        status=status
    )