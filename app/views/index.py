from typing import List, Optional

from fastapi import Request


class JobDescriptionForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.job_description: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.job_description = form.get("job_description")

    async def is_valid(self):
        if not self.job_description or len(self.job_description) < 3:
            self.errors.append("Please write a valid search query")
        if not self.errors:
            return True
        return False
