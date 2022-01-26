from typing import List, Optional

from fastapi import Request


class UserCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        # self.name: Optional[str] = None
        self.email: Optional[str] = None
        self.job_description: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        # self.name = form.get("name")
        self.email = form.get("email")
        self.job_description = form.get("job_description")

    async def is_valid(self):
        return True
