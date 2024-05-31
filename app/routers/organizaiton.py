from fastapi import APIRouter, Form, HTTPException, Request, Depends
from requests.compat import urljoin, quote_plus
from fastapi.responses import JSONResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from ..config import settings
from ..database import get_db
from ..views.user import CreateOrganization, GenerateLoginLink
from ..crud import create_new_org, get_org_by_id, update_org_status, get_org_by_email

from itsdangerous import BadData, URLSafeSerializer
from jose import jwt
from ..oauth2 import Auth
from ..email_alert import Email
from starlette.datastructures import URL
from ..schemas import OrganizationCreate, GenerateOrgLoginLink

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["Organization"])
templates.env.globals['URL'] = URL


@router.post("/create_organization")
def create_organization(request: Request, org: OrganizationCreate, db=Depends(get_db)):
    try:
        created_org = create_new_org(db, org)
        if isinstance(created_org, ValueError):
            return JSONResponse(content={"error": str(created_org)}, status_code=400)
        if isinstance(created_org, BaseException):
            return JSONResponse(content={"error": str(created_org)}, status_code=500)
        if created_org:
            confirmation = Auth.get_confirmation_token(created_org["id"])
            email = Email(
                settings.mail_sender, settings.mail_sender_password
            )
            email.send_confirmation_message(
                confirmation["token"], org.email, is_subscriber=False, subject="Activate your account",
            )
            return JSONResponse(content={
                "success": f"Account created successfully. Verification email has been sent to {org.email}. Please "
                           f"check your inbox and spam folder."}
                , status_code=200)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="An error occurred while creating your account. Try again later")


@router.get("/org/verify/{token}")
async def verify(request: Request, token: str, db=Depends(get_db)):
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
def generate_login_link(request: Request, login_link: GenerateOrgLoginLink, db=Depends(get_db)):
    print(login_link.email)
    try:
        # form = GenerateLoginLink(request)
        # await form.load_data()
        # if await form.is_valid():
        org = get_org_by_email(db, login_link.email)
        if not org:
            # form.errors.append(f"{org['email']} doesn't have an account, create an account first")
            return JSONResponse(
                content={"error": f"{login_link.email} doesn't have an account, create an account first"},
                status_code=400)

        email = Email(settings.mail_sender, settings.mail_sender_password)
        if org.get('is_active'):
            lgn = URLSafeSerializer(settings.secret_key, salt="login")
            login_token = lgn.dumps(org["id"])
            login_url = settings.base_url + "/org/login/{}".format(login_token)
            posting_url = settings.base_url + "/create_post"
            body = "<p>Click this link to create a post</p>"
            email.send_resource(posting_url, "Login link", body, org['email'])
            return JSONResponse(content={
                "success": f"posting link has been sent to {login_link.email}. Please "
                           f"check your inbox and spam folder."}
                , status_code=200)
            # return templates.TemplateResponse(
            #     "post/success.html",
            #     {"request": request, "org": org, "msg": "login link sent successfully"},
            # )
        # form.errors.append(f"{org['email']} doesn't have an active account, try creating and activating your "
        #                    f"account first")
        return JSONResponse(
            content={"error": f"{login_link.email} doesn't have an account, create an account first"},
            status_code=400)
        # return templates.TemplateResponse("post/services.html",
        #                                   {"request": request, "errors": form.__dict__.get("errors")})

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="An error occurred while creating your account. Try again later")
        # form.errors.append(f"an unexpected error occurred, make sure you create an account first before logging in")
        # return templates.TemplateResponse("post/services.html",
        #                                   {"request": request, "errors": form.__dict__.get("errors")})


@router.get("/org/login/{token}")
async def login(request: Request, token: str, response: Response, db=Depends(get_db)):
    try:
        lgn = URLSafeSerializer(settings.secret_key, salt="login")
        org_id = lgn.loads(token)
        org = get_org_by_id(db, org_id)
        if org:
            return RedirectResponse(url=f"/create_post?access_token={token}", status_code=303)
        return templates.TemplateResponse(
            "users/error_page.html",
            {"request": request, "msg": "login-error"})
    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            "users/error_page.html",
            {"request": request, "msg": "Account doesn't exist"})


