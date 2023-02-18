from fastapi import APIRouter, Form, HTTPException, Request, Response, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ..config import settings
from ..database import get_db
from ..views.user import PostItem
from ..crud import create_new_post, get_post_details_by_id, get_org_by_id
from datetime import datetime, timedelta
from dateutil import parser
from itsdangerous import BadData, URLSafeSerializer
from typing import Optional

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["Job"])


@router.get("/create_post/{token}")
def create_post(request: Request,  token: str, db=Depends(get_db)):
    try:
        lgn = URLSafeSerializer(settings.secret_key, salt="login")
        org_id = lgn.loads(token)
        org = get_org_by_id(db, org_id)
        if org:
            return templates.TemplateResponse("post/create_post.html", {"request": request, 'org': org})
        return templates.TemplateResponse(
            "users/error_page.html",
            {"request": request, "msg": "login-error"})
    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            "users/error_page.html",
            {"request": request, "msg": "login-error"})


@router.post("/create_post")
async def create_post(request: Request, db=Depends(get_db)):
    try:
        org = {}
        form = PostItem(request)
        await form.load_data()
        if await form.is_valid():
            if form.end_date and parser.parse(form.end_date).date() < datetime.now().date():
                org['id'] = form.organization_id
                form.__dict__.get("errors").append(
                    "Please check if end date is valid")
                return templates.TemplateResponse("post/create_post.html",
                                                  {"request": request, "org": org,
                                                   "errors": form.__dict__.get("errors")})
            new_item = {'title': form.item_title, 'organization_id': form.organization_id,
                        'organization': form.organization, 'location': form.location,
                        'end_date': form.end_date, 'type': form.item_type, 'category': '',
                        'details': form.item_details}
            item = create_new_post(db, new_item)
            item['url'] = "/" + item['url'].split('/', 1)[1]
            return templates.TemplateResponse(
                "post/success.html", {"request": request, "item": item},
            )
        return templates.TemplateResponse("post/create_post.html", {"request": request, "org": org,
                                                                    "errors": form.__dict__.get("errors")})
    except Exception as e:
        print(e)
        return templates.TemplateResponse("post/create_post.html",
                                          {"request": request, "org": org, "errors": form.__dict__.get("errors")})


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
