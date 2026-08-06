from fastapi import FastAPI

from src.routers import coins_api, coins_ui

app = FastAPI()

app.include_router(coins_api.router)
app.include_router(coins_ui.router)
