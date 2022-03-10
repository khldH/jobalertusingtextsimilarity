from fastapi import (APIRouter, HTTPException, Request)
from fastapi.templating import Jinja2Templates
from itsdangerous import BadData, URLSafeSerializer
from jose import jwt

from ..config import settings
from ..crud import create_new_user_dynamodb  # create_new_user,
from ..crud import get_user_by_email, get_user_by_id, update_user_status
from ..database import dynamodb, dynamodb_web_service
from ..email_alert import Email
# from ..models import User
from ..oauth2 import Auth
from ..schemas import UserCreate
from ..views.user import UserCreateForm

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
        user_model = UserCreate(email=form.email, job_description=form.job_description)
        try:
            # user = create_new_user(user=user_model, db=db)
            dynamodb_user = create_new_user_dynamodb(db, new_user=user_model)
            # print(dynamodb_user)
            confirmation = Auth.get_confirmation_token(dynamodb_user["id"])
            try:
                email = Email(settings.mail_sender, settings.mail_sender_password)
                email.send_confirmation_message(confirmation["token"], form.email)
            except Exception as e:
                return templates.TemplateResponse(
                    "users/error_page.html",
                    {
                        "request": request,
                        "msg": "an error has occurred, email couldn't be send",
                    },
                )
                # raise HTTPException(
                #     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                #     detail="Email couldn't be send. Please try again.",
                # )
            # return responses.RedirectResponse(
            #     "/?msg=registration successful", status_code=status.HTTP_302_FOUND
            # )  # default is post request, to use get request added status code 302
            return templates.TemplateResponse(
                "users/success.html",
                {
                    "request": request,
                    "msg": "registration successful",
                    "email": form.email,
                },
            )

        except ValueError as e:
            form.__dict__.get("errors").append(e)
            return templates.TemplateResponse("users/subscribe.html", form.__dict__)
    return templates.TemplateResponse("users/subscribe.html", form.__dict__)


@router.get("/verify/{token}")
async def verify(request: Request, token: str):
    if settings.is_prod is False:
        db = dynamodb
    else:
        db = dynamodb_web_service
    invalid_token_error = HTTPException(status_code=400, detail="Invalid token")
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=settings.token_algorithm
        )
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Token has expired")
    if payload["scope"] != "registration":
        raise invalid_token_error
    # user_query = db.query(User).filter(User.id == payload["sub"])
    # user = user_query.first()
    user_dynamodb = get_user_by_id(db, user_id=payload["sub"])
    # print(user_dynamodb)
    if not user_dynamodb:
        return templates.TemplateResponse(
            "users/error_page.html",
            {
                "request": request,
                "msg": "User doesn't exist, verification failed, Please subscribe again",
            },
        )

        # raise invalid_token_error
    if user_dynamodb["is_active"]:
        # return responses.RedirectResponse("/?msg=user already verified")
        return templates.TemplateResponse(
            "users/success.html",
            {"request": request, "msg": "user already verified"},
        )
    try:
        update_user_status(db, user_dynamodb["id"])
        # user.is_active = True
        # db.commit()
        # return responses.RedirectResponse("/?msg=successfully verified")
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
