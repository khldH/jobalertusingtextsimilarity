import uuid
from datetime import datetime

from boto3.dynamodb.conditions import Attr, Key
from sqlalchemy.orm import Session

from .models import Job, User
from .schemas import JobCreate, UserCreate


def create_new_user(user: UserCreate, db: Session):
    user = User(email=user.email, job_description=user.job_description)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_new_user_dynamodb(db, new_user: UserCreate):
    table = db.Table("users")
    user = table.scan(FilterExpression=Attr("email").eq(new_user.email))["Items"]
    if user:
        raise ValueError("email already exists")
    dynamodb_user = new_user.dict()
    dynamodb_user["id"] = str(uuid.uuid4())
    dynamodb_user["is_active"] = False
    dynamodb_user["created_at"] = datetime.utcnow().isoformat()
    table.put_item(Item=dynamodb_user)
    return dynamodb_user


def get_user_by_id(db, user_id):
    table = db.Table("users")
    items = table.scan(FilterExpression=Key("id").eq(user_id))["Items"]
    if len(items) > 0:
        return table.scan(FilterExpression=Key("id").eq(user_id))["Items"][0]
    return {}


def update_user_status(db, user_id):
    table = db.Table("users")
    table.update_item(
        Key={"id": user_id},
        UpdateExpression="set is_active = :r",
        ExpressionAttributeValues={
            ":r": True,
        },
        ReturnValues="UPDATED_NEW",
    )


# def create_jobs(job: JobCreate, db: Session):
#     job = Job(**job)
#     db.add(job)
#     db.commit()
#     db.refresh(job)
#     return job


# def get_all_jobs(db: Session):
#     jobs = []
#     jobs_query = db.query(Job).all()
#     for job in jobs_query:
#         j = dict(
#             title=job.title,
#             category=job.category,
#             posted_date=job.posted_date,
#             url=job.url,
#             country=job.country,
#             city=job.city,
#             organization=job.organization,
#             source=job.source,
#         )
#         jobs.append(j)
#     return jobs
