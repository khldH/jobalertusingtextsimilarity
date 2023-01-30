from fastapi import APIRouter, Form, HTTPException, Request
from requests.compat import urljoin, quote_plus
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from ..config import settings
from ..database import dynamodb, dynamodb_web_service
from ..views.user import CreateOrganization, GenerateLoginLink
from ..crud import create_new_org, get_org_by_id, update_org_status, get_org_by_email

from itsdangerous import BadData, URLSafeSerializer
from jose import jwt
from ..oauth2 import Auth
from ..email_alert import Email
from starlette.datastructures import URL
from app.routers.post import post_item

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["Organization"])
templates.env.globals['URL'] = URL


@router.post("/create_organization")
async def create_organization(request: Request):
    if settings.is_prod is False:
        db = dynamodb
    else:
        db = dynamodb_web_service
    try:

        form = CreateOrganization(request)

        await form.load_data()
        if await form.is_valid():
            new_organization = {'user_name': form.user_name, 'organization': form.organization, 'email': form.email}
            created_org = create_new_org(db, new_organization)
            if isinstance(created_org, ValueError):
                form.__dict__.get("errors").append(
                    f"{form.email} email already exists !"
                )
                return templates.TemplateResponse("post/services.html", form.__dict__)
            if created_org:
                confirmation = Auth.get_confirmation_token(created_org["id"])
                email = Email(
                    settings.mail_sender, settings.mail_sender_password
                )
                email.send_confirmation_message(
                    confirmation["token"], form.email, is_subscriber=False, subject="Activate your account",
                )
                return templates.TemplateResponse("post/success.html",
                                                  {"request": request,
                                                   "msg": "registration successful",
                                                   "email": form.email})

    except Exception as e:
        print(e)
        form.__dict__.get("errors").append(
            f"{form.email} an error occurred"
        )
        return templates.TemplateResponse("post/services.html", form.__dict__)


@router.get("/org/verify/{token}")
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
    _org = get_org_by_id(db, org_id=payload["sub"])
    if not _org:
        return templates.TemplateResponse(
            "users/error_page.html",
            {
                "request": request,
                "msg": "User doesn't exist, verification failed, Please create an account first",
            },
        )
    if _org["is_active"]:
        return templates.TemplateResponse(
            "post/create_post.html",
            {"request": request, "org": _org},
        )
    try:
        update_org_status(db, _org["id"])
        return templates.TemplateResponse(
            "post/create_post.html",
            {"request": request, "org": _org},
        )
    except jwt.JWTError:
        return templates.TemplateResponse("post/services.html")


@router.post("/org/generate_login_link")
async def generate_login_link(request: Request):
    if settings.is_prod is False:
        db = dynamodb
    else:
        db = dynamodb_web_service
    try:
        form = GenerateLoginLink(request)
        await form.load_data()
        if await form.is_valid():
            org = get_org_by_email(db, form.email)
            if not org:
                form.errors.append(f"{org['email']} doesn't have an account, try to creating an account first")
                return templates.TemplateResponse("post/services.html",
                                                  {"request": request, "errors": form.__dict__.get("errors")})

            email = Email(settings.mail_sender, settings.mail_sender_password)
            if org.get('is_active'):
                lgn = URLSafeSerializer(settings.secret_key, salt="login")
                login_token = lgn.dumps(org["id"])
                login_url = settings.base_url+"/org/login/{}".format(login_token)
                body = "<p>Click this link to login</p>"
                email.send_resource(login_url, "Login link", body, org['email'])
                return templates.TemplateResponse(
                    "post/success.html",
                    {"request": request, "org": org, "msg": "login link sent successfully"},
                )
            form.errors.append(f"{org['email']} doesn't have an active account, try creating and activating your "
                               f"account first")
            return templates.TemplateResponse("post/services.html", {"request": request,"errors":form.__dict__.get("errors")})

    except Exception as e:
        print(e)
        form.errors.append(f"an unexpected error occurred, make sure you create an account first before logging in")
        return templates.TemplateResponse("post/services.html", {"request": request,"errors":form.__dict__.get("errors")})


@router.get("/org/login/{token}")
async def login(request: Request, token: str):
    if settings.is_prod is False:
        db = dynamodb
    else:
        db = dynamodb_web_service

    try:
        lgn = URLSafeSerializer(settings.secret_key, salt="login")
        org_id = lgn.loads(token)
        org = get_org_by_id(db, org_id)
        if org:
            return RedirectResponse(url=f"/create_post/{token}", status_code=303)
        return templates.TemplateResponse(
            "users/error_page.html",
            {"request": request, "msg": "login-error"})
    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            "users/error_page.html",
            {"request": request, "msg": "login-error"})
        # # root_url = settings.base_url + '/create_post/'
        # # print(root_url)
        # # url = urljoin(root_url, quote_plus(org['id']))
        # # print(url)
        # return templates.TemplateResponse(
        #     "post/create_post.html",
        #     {"request": request, "msg": "login successful"},
        # )
