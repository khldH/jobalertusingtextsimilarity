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
        self.first_name: Optional[str] = None
        self.last_name: Optional[str] = None
        self.job_title: Optional[str] = None
        self.qualification: Optional[str] = None
        self.experience: Optional[str] = None
        self.user_location: Optional[str] = None
        self.skills: Optional[list] = []
        # self.frequency:Optional[str] = 'Daily'

    async def load_data(self):
        form = await self.request.form()
        self.id = form.get("id")
        self.job_description = form.get("job_description")
        self.is_all = form.get("is_all")
        self.is_active = form.get("is_active")
        self.follows = form.get("follows")
        self.first_name = form.get("first_name")
        self.last_name = form.get("last_name")
        self.job_title = form.get("item_title")
        self.qualification = form.get("qualification")
        self.experience = form.get("experience")
        self.user_location = form.get("user_location")
        self.skills = form.get("skills")

        # self.frequency = form.get('frequency')

    async def is_valid(self):
        return True


class PostItem:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.organization_id: Optional[str] = None
        self.item_title: Optional[str] = None
        self.organization: Optional[str] = None
        self.item_type: Optional[str] = None
        self.location: Optional[str] = None
        self.end_date: Optional[str] = None
        self.item_details: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.organization_id = form.get("org_id")
        self.item_title = form.get("item_title")
        self.organization = form.get("organization")
        self.item_type = form.get("item_type")
        self.location = form.get("location")
        self.end_date = form.get("end_date")
        self.item_details = form.get("item_details")

    async def is_valid(self):
        # if not self.organization_id:
        #     self.errors.append("Organization must have a valid id")
        if not self.item_title or not len(self.item_title) >= 4:
            self.errors.append("A valid title is required")
        if not self.item_details or not len(self.item_details) >= 20:
            self.errors.append("Post details is too short, Please add in more info to your post")
        if not self.errors:
            return True
        return False


class CreateOrganization:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.user_name: Optional[str] = None
        self.organization: Optional[str] = None
        self.email: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.user_name = form.get("user_name")
        self.organization = form.get("organization")
        self.email = form.get("email")

    async def is_valid(self):
        return True


class GenerateLoginLink:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.email: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.email = form.get("email")

    async def is_valid(self):
        return True
