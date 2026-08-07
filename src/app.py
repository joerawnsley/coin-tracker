import os

from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from src.routers import coins_api, coins_ui

limiter = Limiter(
    key_func=get_remote_address, default_limits=["5/10 seconds", "20/minute"]
)

app = FastAPI()

if os.getenv("DB_ENVIRONMENT") == "prod":
    app.add_middleware(SlowAPIMiddleware)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(coins_api.router)
app.include_router(coins_ui.router)
