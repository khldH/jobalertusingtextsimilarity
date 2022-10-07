import re
from collections import Counter
from pathlib import Path
from typing import Optional
from dateutil import parser

from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import dynamodb, dynamodb_web_service
from app.services.search.document import Document

# from ..services.scrappers.scrape_jobs import create_documents
from ..services.search.document_search import DocumentSearch
from ..views.index import JobDescriptionForm
import numpy as np

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="", tags=["home"])


# router.mount("/static", StaticFiles(directory="app/static"), name="static")

@router.get("/")
def home(request: Request):
    try:
        if settings.is_prod is False:
            table = dynamodb.Table("jobs")
        else:
            table = dynamodb_web_service.Table("jobs")

        jobs = table.scan()["Items"]
        # orgs = []
        fully_remote = []
        for job in jobs:
            # orgs.append(job["organization"].strip())
            if job['location'] == 'Anywhere in the World':
                fully_remote.append(job)

        fully_remote = sorted(fully_remote, key=lambda item: parser.parse(item["posted_date"]), reverse=True)
        # break
        # common_orgs = Counter(orgs).most_common(15)
        # common_orgs = [name[0].replace(",", "") for name in common_orgs if name[0] != ""]
        # more_orgs = [org for org in orgs if org not in common_orgs and org != ""]
        return templates.TemplateResponse(
            "home/index.html",
            {
                "request": request,
                # "common_orgs": common_orgs,
                # "more_orgs": more_orgs,
                "remote_jobs": fully_remote
            },
        )
    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            "users/error_page.html",
            {"request": request, "msg": "an error has occurred, Please try again"},
        )


@router.get("/remote-jobs")
def get_all_remote_jobs(request: Request):
    try:
        if settings.is_prod is False:
            table = dynamodb.Table("jobs")
        else:
            table = dynamodb_web_service.Table("jobs")

        jobs = table.scan()["Items"]
        fully_remote = []
        for job in jobs:
            if job['location'] == 'Anywhere in the World':
                fully_remote.append(job)
        fully_remote = sorted(fully_remote, key=lambda item: parser.parse(item["posted_date"]), reverse=True)
        return templates.TemplateResponse(
            "home/remote_jobs.html",
            {
                "request": request,
                "remote_jobs": fully_remote
            })
    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            "users/error_page.html",
            {"request": request, "msg": "an error has occurred, Please try again"})


@router.get("/search/")
def search(request: Request, query: Optional[str] = None):
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
            return templates.TemplateResponse("home/index.html", {"request": request, "query": query})
        return templates.TemplateResponse("home/index.html")
    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            "users/error_page.html",
            {"request": request, "msg": "an error has occurred, Please try again"},
        )
