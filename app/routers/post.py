from fastapi import APIRouter, Form, HTTPException, Request, Response, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import responses, status
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from ..config import settings
from ..database import get_db
from ..views.user import PostItem
from ..crud import create_new_post, get_post_details_by_id, get_org_by_id
from datetime import datetime, timedelta
from dateutil import parser
from itsdangerous import BadData, URLSafeSerializer
from typing import Optional
from ..schemas import VerificationToken, PostCreate

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["Job"])


@router.get("/create_post")
def create_post(request: Request):
    return templates.TemplateResponse("post/create_post.html", {"request": request})


@router.post("/create_post")
def create_post(request: Request, post: PostCreate, db=Depends(get_db)):
    # print(post.post_details)
    try:
        new_post = create_new_post(db, post)
        print(new_post)
        new_post['url'] = "/" + new_post['url'].split('/', 1)[1]
        post_url = f"/post/{new_post['id']}"
        return JSONResponse(content={"url": post_url}, status_code=200)
    except Exception as e:
        print(e)
        return templates.TemplateResponse("post/create_post.html", {"request": request})


@router.get("/post/{item_id}")
def get_post_details(request: Request, item_id: str, db=Depends(get_db)):
    try:
        item = get_post_details_by_id(db, item_id)
        if item:
            # print(item)
            item['days_since_posted'] = (datetime.now().date() - parser.parse(item['posted_date']).date()).days
            if item['end_date']:
                item['closes_on'] = (parser.parse(item['end_date']).date() - datetime.now().date()).days

            return templates.TemplateResponse(
                "post/post_details.html",
                {"request": request, "item": item},
            )
    except Exception as e:
        print(e)
    return templates.TemplateResponse(
        "users/error_page.html",
        {
            "request": request,
            "msg": "Post not found",
        },
    )
