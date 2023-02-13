from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["Services"])


@router.get("/services")
def subscribe(request: Request):
    return templates.TemplateResponse("post/services.html", {"request": request})