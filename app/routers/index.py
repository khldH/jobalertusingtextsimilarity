import re
from collections import Counter
from pathlib import Path
from typing import Optional

import numpy as np
from dateutil import parser
from fastapi import APIRouter, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import get_db
from app.services.search.document import Document

# from ..services.scrappers.scrape_jobs import create_documents
from ..services.search.document_search import DocumentSearch
from ..views.index import JobDescriptionForm

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="", tags=["home"])


# router.mount("/static", StaticFiles(directory="app/static"), name="static")


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse("home/index.html", {"request": request})


@router.get("/remote-jobs")
def get_all_remote_jobs(request: Request, db=Depends(get_db)):
    try:
        table = db.Table("jobs")
        jobs = table.scan()["Items"]
        fully_remote = []
        for job in jobs:
            if job["location"] == "Anywhere in the World":
                fully_remote.append(job)

        fully_remote = sorted(
            fully_remote,
            key=lambda item: parser.parse(item["posted_date"]),
            reverse=True,
        )

        return templates.TemplateResponse("home/remote_jobs.html", {"request": request, "remote_jobs": fully_remote})
    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            "users/error_page.html",
            {"request": request, "msg": "an error has occurred, Please try again"},
        )


@router.get("/search/")
def search(request: Request, db=Depends(get_db), query: Optional[str] = None):
    # form = JobDescriptionForm(request)
    # await form.load_data()
    # if await form.is_valid():
    # documents = create_documents()
    try:
        posts = db.Table("posts").scan()["Items"]
        jobs = db.Table("jobs").scan()["Items"]
        jobs = jobs + posts
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
            return templates.TemplateResponse("home/index.html", {"request": request, "query": query})
        return templates.TemplateResponse("home/index.html")
    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            "users/error_page.html",
            {"request": request, "msg": "an error has occurred, Please try again"},
        )
