import boto3
from .config import settings


def get_db():
    if not settings.is_prod:
        settings.endpoint_url = "http://localhost:8000"
        return boto3.resource("dynamodb", region_name=settings.aws_region_name, endpoint_url=settings.endpoint_url)
    return boto3.resource(
        "dynamodb",
        region_name=settings.aws_region_name,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )
