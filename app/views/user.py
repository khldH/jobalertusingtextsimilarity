from typing import List, Optional

from fastapi import Request


class UserCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.email: Optional[str] = None
        self.job_description: Optional[str] = None
        self.is_all: Optional[bool] = False

    async def load_data(self):
        form = await self.request.form()
        self.email = form.get("email")
        self.job_description = form.get("job_description")
        self.is_all = form.get("is_all")

    async def is_valid(self):
        return True


class UpdateJobAlertForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.id: Optional[str] = None
        self.job_description: Optional[str] = None
        self.is_all: Optional[bool] = False
        self.is_active: Optional[bool] = False
        self.follows: Optional[List] = []
        # self.frequency:Optional[str] = 'Daily'

    async def load_data(self):
        form = await self.request.form()
        self.id = form.get("id")
        self.job_description = form.get("job_description")
        self.is_all = form.get("is_all")
        self.is_active = form.get("is_active")
        self.follows = form.get("follows")
        # self.frequency = form.get('frequency')

    async def is_valid(self):
        return True
