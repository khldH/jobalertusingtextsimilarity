import re
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import dynamodb, dynamodb_web_service
from app.services.search.document import Document

# from ..services.scrappers.scrape_jobs import create_documents
from ..services.search.document_search import DocumentSearch
from ..views.index import JobDescriptionForm

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="", tags=["home"])


# router.mount("/static", StaticFiles(directory="app/static"), name="static")


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home/index.html", {"request": request})


@router.get("/search/")
async def search(request: Request, query: Optional[str] = None):
    # form = JobDescriptionForm(request)
    # await form.load_data()
    # if await form.is_valid():
    # documents = create_documents()
    try:
        if settings.is_prod is False:
            table = dynamodb.Table("jobs")
        else:
            table = dynamodb_web_service.Table("jobs")

        jobs = table.scan()["Items"]

        documents = []
        for job in jobs:
            documents.append(Document(**job))
        try:
            document_search = DocumentSearch(documents)
            query = re.sub("[^A-Za-z0-9]+", " ", query)
            matched_jobs = []
            if len(query) > 1:
                matched_jobs = document_search.search(query)
            return templates.TemplateResponse(
                "home/index.html",
                {"request": request, "jobs": matched_jobs, "query": query},
            )
        except ValueError:
            return templates.TemplateResponse(
                "home/index.html", {"request": request, "query": query}
            )
        return templates.TemplateResponse("home/index.html")
    except Exception as e:
        return templates.TemplateResponse(
            "users/error_page.html", {"request": request,
                                      "msg": "an error has occurred, Please try again"}
        )

