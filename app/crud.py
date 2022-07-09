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


def create_new_user(db, new_user: UserCreate):
    table = db.Table("users")
    try:
        user = table.scan(FilterExpression=Attr("email").eq(new_user.email))["Items"]
        if user:
            user = user[0]
            if user["is_active"] and user["job_description"] is not None:
                return ValueError("email already exists")
            updated_user = table.update_item(
                Key={"id": user["id"]},
                UpdateExpression="set job_description = :r, is_active = :s",
                ExpressionAttributeValues={
                    ":r": new_user.job_description,
                    ":s": False,
                },
                ReturnValues="ALL_NEW",
            )["Attributes"]
            return updated_user

        _user = new_user.dict()
        _user["id"] = str(uuid.uuid4())
        # _user["is_active"] = False
        # _user['frequency'] = 'Daily'
        _user["created_at"] = datetime.utcnow().isoformat()
        # _user["modified_at"] = None
        table.put_item(Item=_user)
        return _user
    except Exception as e:
        return {}


def get_user_by_id(db, user_id):
    table = db.Table("users")
    items = table.scan(FilterExpression=Key("id").eq(user_id))["Items"]
    if len(items) > 0:
        return items[0]
    return {}


def update_user_status(db, user_id, status=True):
    table = db.Table("users")
    table.update_item(
        Key={"id": user_id},
        UpdateExpression="set is_active = :r, modified_at =:d",
        ExpressionAttributeValues={
            ":r": status,
            ":d": datetime.utcnow().isoformat()
        },
        ReturnValues="UPDATED_NEW",
    )


def get_user_by_email(db, email):
    table = db.Table("users")
    user = table.scan(FilterExpression=Attr("email").eq(email))["Items"]
    if len(user) > 0:
        return user[0]
    return {}


def update_job_alert(db, user):
    table = db.Table("users")
    updated_job_alert = table.update_item(
        Key={"id": user["id"]},
        UpdateExpression="set is_active = :s, job_description = :j, follows = :f, is_all = :a, modified_at =:d",
        ExpressionAttributeValues={
            ":s": user["is_active"],
            ":j": user["job_description"],
            ":f": user["follows"],
            ":a": user["is_all"],
            ":d": datetime.utcnow().isoformat()
        },
        ReturnValues="ALL_NEW",
    )
    return updated_job_alert["Attributes"]
