from fastapi import APIRouter, Form, status
from fastapi.responses import RedirectResponse

from src.auth import get_user, hash_password, user_db

router = APIRouter()