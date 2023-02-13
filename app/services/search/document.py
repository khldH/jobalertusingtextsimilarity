from typing import Optional

from pydantic import BaseModel


class Document(BaseModel):
    """job"""

    id: str
    title: Optional[str]
    url: Optional[str]
    posted_date: Optional[str]
    category: Optional[str]
    organization: Optional[str]
    location: Optional[str]
    source: Optional[str]
    type: Optional[str]

    @property
    def full_text(self):
        return " ".join(
            [self.title, self.category, self.type, self.location, self.organization]
        )
