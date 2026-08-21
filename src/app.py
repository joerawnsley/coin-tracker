import os

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.limiter import limiter, too_many_requests_handler
from src.routers import coins_api, coins_ui

app = FastAPI()

app.include_router(coins_api.router)
app.include_router(coins_ui.router)

if os.getenv("DB_ENVIRONMENT") == "prod":
    app.add_middleware(SlowAPIMiddleware)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, too_many_requests_handler)
