import uuid
from src.database_models import User

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

def coin_to_dict(coin):
    return dict(
        id = coin.id,
        coinName = coin.coin_name,
        coinPath = coin.coin_path,
        duties = set([duty.duty_number for duty in coin.duties]),
        isComplete = coin.is_complete
    )

def duty_to_dict(duty):
    return dict(
        id = duty.id,
        dutyNumber = duty.duty_number,
        description = duty.description,
        coins = set([coin.coin_name for coin in duty.coins])
    )


