import boto3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

# SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
#
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
#
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# Base = declarative_base()
#
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


def get_db():
    if not settings.is_prod:
        settings.endpoint_url = "http://localhost:8000"
        return boto3.resource("dynamodb", region_name=settings.aws_region_name, endpoint_url=settings.endpoint_url)
    return boto3.resource(
        "dynamodb",
        region_name=settings.region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


dynamodb_web_service = boto3.resource(
    "dynamodb",
    region_name=settings.aws_region_name,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)

dynamodb = boto3.resource("dynamodb", region_name="eu-west-2", endpoint_url="http://localhost:8000")
