import time
from typing import List, Optional
from pydantic import BaseModel

import joblib
import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from itsdangerous import BadData, URLSafeSerializer
from jose import jwt
from pydantic import ValidationError

from app.database import get_db

from ..config import settings
from ..crud import create_new_user  # create_new_user,
from ..crud import (get_user_by_email, get_user_by_id, update_job_alert,
                    update_user_status)
from ..email_alert import Email
# from ..models import User
from ..oauth2 import Auth
from ..schemas import UserCreate
from ..views.user import UpdateJobAlertForm, UserCreateForm

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["Users"])

spam_detector = {}


@router.on_event("startup")
def load_spam_detector():
    spam_detector["model"] = joblib.load("app/services/spam_detector/spam_detector.pkl")


@router.get("/subscribe")
def subscribe(request: Request):
    return templates.TemplateResponse("users/subscribe.html", {"request": request})


# class Job(BaseModel):
#     email: Optional[str] = None
#     job_description: Optional[str] = None
#
#
# @router.post("/jobs_test")
# def create_job(request: Request, user: UserCreate):
#     print(user)
#     # return {"message": "Job created successfully"}


@router.post("/subscribe")
def subscribe(request: Request, user: UserCreate, db=Depends(get_db)):
    try:
        if not user.job_description and user.is_all is False:
            return JSONResponse(content={"error": "Please either select 'Send all new jobs to my email' or write your "
                                                  "criteria in the space provided"},
                                status_code=400)
        spam_detector_model = spam_detector["model"]
        user_df = pd.DataFrame([user.dict()])
        prediction = spam_detector_model.predict_proba(user_df)[:, 1][0]
        is_spam = False if prediction < 0.63 or user.is_all else True
        _user = create_new_user(db, new_user=user, is_spam=is_spam)
        if isinstance(_user, ValueError):
            return JSONResponse(content={"error": str(_user)}, status_code=400)
        if _user:
            confirmation = Auth.get_confirmation_token(_user["id"])
            try:
                print("prediction", prediction)
                if not is_spam:
                    email = Email(settings.mail_sender, settings.mail_sender_password)
                    email.send_confirmation_message(confirmation["token"], user.email)
                return JSONResponse(content={
                    "success": f"Successfully subscribed. Verification email has been sent to {user.email}. Please "
                               f"check your inbox and spam folder."}
                    , status_code=200)
            except Exception as e:
                print(e)
                return JSONResponse(content={"error": f"an error occurred, please try again later"}, status_code=400)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="An error occurred while creating your account. Try again later")
#
    # return templates.TemplateResponse("home/index.html", form.__dict__)


@router.get("/verify/{token}")
async def verify(request: Request, token: str, db=Depends(get_db)):
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
        body = "<p>Thank you for verifying your email. Click this link to download your free cv template</p>"
        email = Email(settings.mail_sender, settings.mail_sender_password)
        # email.send_resource(
        #     resource="https://drive.google.com/uc?export=download&id=1aJGlSLjlgHU62awmazd-COzt6IWgcq32",
        #     subject="Download your free example CV",
        #     body=body,
        #     mail_to=_user["email"],
        # )
        return templates.TemplateResponse(
            "users/success.html",
            {"request": request, "msg": "verification successful"},
        )
    except jwt.JWTError:
        return templates.TemplateResponse("users/subscribe.html")


@router.get("/unsubscribe/{token}")
async def unsubscribe(request: Request, token: str, db=Depends(get_db)):
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
            {"request": request, "msg": "error-unsubscribe"},
        )


@router.get("/edit/{token}", response_class=HTMLResponse)
async def edit_job_alert(request: Request, token: str, db=Depends(get_db)):
    # if settings.is_prod is False:
    #     db = dynamodb
    # else:
    #     db = dynamodb_web_service

    try:
        e = URLSafeSerializer(settings.secret_key, salt="edit")
        email = e.loads(token)
        user = get_user_by_email(db, email)
        return templates.TemplateResponse(
            "users/update_job_alert.html",
            {"request": request, "msg": "update job alert", "user": user},
        )

    except BadData as e:
        print(e)
        return templates.TemplateResponse(
            "users/error_page.html",
            {"request": request, "msg": "an error occurred, can't update your alert now "},
        )


@router.post("/edit")
async def edit_job_alert(request: Request, follows: List[str] = Form(...), db=Depends(get_db)):
    form = (UpdateJobAlertForm(request),)
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
            user["first_name"] = form.first_name
            user["last_name"] = form.last_name
            user["item_title"] = form.job_title
            user["qualification"] = form.qualification
            user["experience"] = form.experience
            user["user_location"] = form.user_location
            user["skills"] = form.skills
            updated_alert = update_job_alert(db, user)
            email = Email(settings.mail_sender, settings.mail_sender_password)
            if (
                    updated_alert["is_active"]
                    and updated_alert["first_name"]
                    and updated_alert["last_name"]
                    and updated_alert["user_location"]
                    and updated_alert["qualification"]
            ):
                body = "<p>Thank you for updating your profile<br>Download your free CV template here " "<br></p>"

                email.send_resource(
                    "https://drive.google.com/uc?export=download&id=1aJGlSLjlgHU62awmazd-COzt6IWgcq32",
                    "Download your free CV template",
                    body,
                    updated_alert["email"],
                )
            # if updated_alert["user_location"]:
            #
            #     body = "<p>Thank you for updating your location<br>Download your free cover letter template here " \
            #            "<br></p> "
            #
            #     email.send_resource(
            #         "https://drive.google.com/uc?export=download&id=1SnH0_keAVPUep8BZEzZQFWQGW9LD0Bug",
            #         "Download your free cover letter template",
            #         body,
            #         updated_alert["email"],
            #     )

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
async def follow_organization(request: Request, email: str = Form(...), org: List[str] = Form(...), db=Depends(get_db)):
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
