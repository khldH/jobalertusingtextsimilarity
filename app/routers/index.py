import re
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
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
    table = dynamodb.Table("jobs")
    jobs = table.scan()["Items"]
    documents = []
    for job in jobs:
        documents.append(Document(**job))
    document_search = DocumentSearch(documents)
    query = re.sub("[^A-Za-z0-9]+", " ", query)
    matched_jobs = []
    if len(query) > 1:
        matched_jobs = document_search.search(query)
    return templates.TemplateResponse(
        "home/index.html",
        {"request": request, "jobs": matched_jobs, "query": query},
    )
    return templates.TemplateResponse("home/index.html")
