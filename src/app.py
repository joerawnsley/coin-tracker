from fastapi import FastAPI
from src.routers import coins_api, coins_ui, auth_api

app = FastAPI()

app.include_router(coins_api.router)
app.include_router(coins_ui.router)
app.include_router(auth_api.router)