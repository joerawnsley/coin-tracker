import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from peewee import DoesNotExist
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.limiter import limiter, too_many_requests_handler
from src.routers import coins_api, coins_ui

app = FastAPI()

app.include_router(coins_api.router)
app.include_router(coins_ui.router)


@app.exception_handler(DoesNotExist)
def not_found_handler(request: Request, exc: DoesNotExist):
    model_name = type(exc).__name__.removesuffix("DoesNotExist")
    return JSONResponse(
        status_code=404,
        content={"detail": f"{model_name} not found"},
    )

if os.getenv("DB_ENVIRONMENT") == "prod":
    app.add_middleware(SlowAPIMiddleware)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, too_many_requests_handler)
