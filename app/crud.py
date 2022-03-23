import uuid
from datetime import datetime

from boto3.dynamodb.conditions import Attr, Key
from sqlalchemy.orm import Session

# from .models import Job, User
from .schemas import JobCreate, UserCreate

# def create_new_user(user: UserCreate, db: Session):
#     user = User(email=user.email, job_description=user.job_description)
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return user


def create_new_user_dynamodb(db, new_user: UserCreate):
    table = db.Table("users")
    try:
        user = table.scan(FilterExpression=Attr("email").eq(new_user.email))["Items"]
        if user:
            user = user[0]
            print(user)
            if user["is_active"]:
                raise ValueError("email already exists")
            updated_user = table.update_item(
                Key={"id": user["id"]},
                UpdateExpression="set job_description = :r",
                ExpressionAttributeValues={
                    ":r": new_user.job_description,
                },
                ReturnValues="ALL_NEW",
            )["Attributes"]
            return updated_user

        dynamodb_user = new_user.dict()
        dynamodb_user["id"] = str(uuid.uuid4())
        dynamodb_user["is_active"] = False
        # dynamodb_user['frequency'] = 'Daily'
        dynamodb_user["created_at"] = datetime.utcnow().isoformat()
        table.put_item(Item=dynamodb_user)
        return dynamodb_user
    except Exception as e:
        return {}


def get_user_by_id(db, user_id):
    table = db.Table("users")
    items = table.scan(FilterExpression=Key("id").eq(user_id))["Items"]
    if len(items) > 0:
        return table.scan(FilterExpression=Key("id").eq(user_id))["Items"][0]
    return {}


def update_user_status(db, user_id, status=True):
    table = db.Table("users")
    table.update_item(
        Key={"id": user_id},
        UpdateExpression="set is_active = :r",
        ExpressionAttributeValues={
            ":r": status,
        },
        ReturnValues="UPDATED_NEW",
    )


def get_user_by_email(db, email):
    table = db.Table("users")
    user = table.scan(FilterExpression=Attr("email").eq(email))["Items"][0]
    return user


def update_job_alert(db, user_id, status, job_description):
    table = db.Table("users")
    table.update_item(
        Key={"id": user_id},
        UpdateExpression="set is_active = :s, job_description = :j",
        ExpressionAttributeValues={
            ":s": status,
            ":j":job_description,
        },
        ReturnValues="UPDATED_NEW",
    )


