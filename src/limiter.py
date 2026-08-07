from fastapi import Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address, default_limits=["7/10 seconds", "20/minute"]
)

templates = Jinja2Templates(directory="src/templates")


def too_many_requests_handler(request: Request, exc):
    if request.url.path == "/login":
        return RedirectResponse(
            url="/login?error=Too many login attempts",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    else:
        return templates.TemplateResponse(request=request, name="429.html", status_code=429)
