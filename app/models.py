import uuid

from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    # name = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    job_description = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Job(Base):
    __tablename__ = "jobs"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    # name = Column(String, nullable=True)
    title = Column(String, nullable=False, unique=True)
    category = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    url = Column(String, nullable=True)
    posted_date = Column(String, nullable=True)
    source = Column(String, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
