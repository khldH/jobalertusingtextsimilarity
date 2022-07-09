from typing import List

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from itsdangerous import BadData, URLSafeSerializer
from jose import jwt
from pydantic import ValidationError
from ..config import settings
from ..crud import create_new_user  # create_new_user,
from ..crud import (
    get_user_by_email,
    get_user_by_id,
    update_job_alert,
    update_user_status,
)
from ..database import dynamodb, dynamodb_web_service
from ..email_alert import Email

# from ..models import User
from ..oauth2 import Auth
from ..schemas import UserCreate
from ..views.user import UpdateJobAlertForm, UserCreateForm

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["Users"])


@router.get("/subscribe")
def subscribe(request: Request):
    return templates.TemplateResponse("users/subscribe.html", {"request": request})


@router.post("/subscribe")
async def subscribe(request: Request):
    if settings.is_prod is False:
        db = dynamodb
    else:
        db = dynamodb_web_service
    form = UserCreateForm(request)
    await form.load_data()
    if await form.is_valid():

        try:
            user_model = UserCreate(
                email=form.email,
                job_description=form.job_description,
                is_all=form.is_all,
            )
            _user = create_new_user(db, new_user=user_model)
            if isinstance(_user, ValueError):
                form.__dict__.get("errors").append(f"{form.email} email already exists !")
                return templates.TemplateResponse("home/index.html", form.__dict__)
            if _user:
                confirmation = Auth.get_confirmation_token(_user["id"])
                try:
                    email = Email(settings.mail_sender, settings.mail_sender_password)
                    email.send_confirmation_message(confirmation["token"], form.email)
                    return templates.TemplateResponse(
                        "users/success.html",
                        {
                            "request": request,
                            "msg": "registration successful",
                            "email": form.email,
                        },
                    )
                except Exception as e:
                    print(e)
                    return templates.TemplateResponse(
                        "users/error_page.html",
                        {
                            "request": request,
                            "msg": "an error has occurred, email couldn't be send,please make sure your email is "
                            "correct",
                        },
                    )

        except ValidationError as e:
            print(e)
            form.__dict__.get("errors").append(f"{form.email} is not a valid email address")
            return templates.TemplateResponse("home/index.html", form.__dict__)

    return templates.TemplateResponse("home/index.html", form.__dict__)


@router.get("/verify/{token}")
async def verify(request: Request, token: str):
    if settings.is_prod is False:
        db = dynamodb
    else:
        db = dynamodb_web_service
    invalid_token_error = HTTPException(status_code=400, detail="Invalid token")
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=settings.token_algorithm)
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Token has expired")
    if payload["scope"] != "registration":
        raise invalid_token_error
    _user = get_user_by_id(db, user_id=payload["sub"])
    if not _user:
        return templates.TemplateResponse(
            "users/error_page.html",
            {
                "request": request,
                "msg": "User doesn't exist, verification failed, Please subscribe again",
            },
        )
    if _user["is_active"]:
        return templates.TemplateResponse(
            "users/success.html",
            {"request": request, "msg": "user already verified"},
        )
    try:
        update_user_status(db, _user["id"])
        # email = Email(settings.mail_sender, settings.mail_sender_password)
        # email.send_resource(
        #     "https://drive.google.com/uc?export=download&id=1ALOG-4yBvIOeaIRN32lXH04fY499yVh-",
        #     _user["email"]
        # )
        return templates.TemplateResponse(
            "users/success.html",
            {"request": request, "msg": "verification successful"},
        )
    except jwt.JWTError:
        return templates.TemplateResponse("users/subscribe.html")


@router.get("/unsubscribe/{token}")
async def unsubscribe(request: Request, token: str):
    if settings.is_prod is False:
        db = dynamodb
    else:
        db = dynamodb_web_service
    s = URLSafeSerializer(settings.secret_key, salt="unsubscribe")

    try:
        email = s.loads(token)
        user = get_user_by_email(db, email)
        update_user_status(db, user["id"], status=False)
        return templates.TemplateResponse(
            "users/success.html",
            {"request": request, "msg": "successfully unsubscribed"},
        )
    except BadData:
        return templates.TemplateResponse(
            "users/error_page.html",
            {"request": request, "msg": "error-unsubscirbe"},
        )


@router.get("/edit/{token}", response_class=HTMLResponse)
async def edit_job_alert(request: Request, token: str):
    if settings.is_prod is False:
        db = dynamodb
    else:
        db = dynamodb_web_service

    try:
        e = URLSafeSerializer(settings.secret_key, salt="edit")
        email = e.loads(token)
        user = get_user_by_email(db, email)
        return templates.TemplateResponse(
            "users/update_job_alert.html",
            {"request": request, "msg": "update job alert", "user": user},
        )

    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            "users/error_page.html",
            {"request": request, "msg": "error-unsubscirbe"},
        )


@router.post("/edit")
async def edit_job_alert(request: Request, follows: List[str] = Form(...)):
    if settings.is_prod is False:
        db = dynamodb
    else:
        db = dynamodb_web_service
    form = UpdateJobAlertForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            user = {}
            status = True
            is_all = True
            if form.is_active is None:
                status = False
            if form.is_all is None:
                is_all = False
            user["id"] = form.id
            user["is_active"] = status
            user["job_description"] = form.job_description
            user["is_all"] = is_all
            user["follows"] = follows
            update_job_alert(db, user)
            return templates.TemplateResponse(
                "users/success.html",
                {"request": request, "msg": "successfully updated"},
            )

        except Exception as e:
            return templates.TemplateResponse(
                "users/error_page.html",
                {
                    "request": request,
                    "msg": "job alert couldn't be updated, please try again",
                },
            )


@router.post("/follow")
async def follow_organization(request: Request, email: str = Form(...), org: List[str] = Form(...)):
    if settings.is_prod is False:
        db = dynamodb
    else:
        db = dynamodb_web_service

    try:
        user = get_user_by_email(db, email)
        if not user:
            new_user = UserCreate(email=email)
            new_user.follows.extend(org)
            _user = create_new_user(db, new_user)
            confirmation = Auth.get_confirmation_token(_user["id"])
            try:
                email = Email(settings.mail_sender, settings.mail_sender_password)
                email.send_confirmation_message(confirmation["token"], new_user.email)
            except Exception as e:
                print(e)
                return templates.TemplateResponse(
                    "users/error_page.html",
                    {
                        "request": request,
                        "msg": "an error has occurred, email couldn't be send,please make sure your email is "
                        "correct",
                    },
                )
            return templates.TemplateResponse(
                "users/success.html",
                {
                    "request": request,
                    "msg": "registration successful",
                    "email": new_user.email,
                },
            )
        user.setdefault("follows", [])
        user["follows"] = org
        updated_user = update_job_alert(db, user)
        if not updated_user["is_active"]:
            try:
                confirmation = Auth.get_confirmation_token(updated_user["id"])
                email = Email(settings.mail_sender, settings.mail_sender_password)
                email.send_confirmation_message(confirmation["token"], updated_user["email"])
            except Exception as e:
                print(e)
                return templates.TemplateResponse(
                    "users/error_page.html",
                    {
                        "request": request,
                        "msg": "an error has occurred, email couldn't be send,please make sure your email is "
                        "correct",
                    },
                )
            return templates.TemplateResponse(
                "users/success.html",
                {
                    "request": request,
                    "msg": "registration successful",
                    "email": updated_user["email"],
                },
            )
        return templates.TemplateResponse(
            "users/success.html",
            {"request": request, "msg": "successful follow", "orgs": org},
        )
    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            "users/error_page.html",
            {
                "request": request,
                "msg": "Action couldn't be completed, please try again",
            },
        )
