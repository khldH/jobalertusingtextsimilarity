import uuid
from datetime import datetime

from boto3.dynamodb.conditions import Attr, Key
from sqlalchemy.orm import Session

# from .models import Job, User
from .schemas import JobCreate, UserCreate
from app.config import settings


# def create_new_user(user: UserCreate, db: Session):
#     user = User(email=user.email, job_description=user.job_description)
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return user


def create_new_user(db, new_user: UserCreate, is_spam=False):
    try:
        if not is_spam:
            table = db.Table("users")
            user = table.scan(FilterExpression=Attr("email").eq(new_user.email))[
                "Items"
            ]
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
            _user["created_at"] = datetime.utcnow().isoformat()
            table.put_item(Item=_user)
            return _user
        table = db.Table("spam_users")
        _user = new_user.dict()
        _user["id"] = str(uuid.uuid4())
        _user["created_at"] = datetime.utcnow().isoformat()
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
        ExpressionAttributeValues={":r": status, ":d": datetime.utcnow().isoformat()},
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
        UpdateExpression="set is_active = :s, "
                         "job_description = :j, "
                         "follows = :f, "
                         "is_all = :a, "
                         "first_name = :fn, "
                         "last_name = :ln, "
                         "item_title = :jt, "
                         "qualification = :q, "
                         "experience= :ex, "
                         "user_location= :lc, "
                         "skills= :sk, "
                         "modified_at =:d",
        ExpressionAttributeValues={
            ":s": user["is_active"],
            ":j": user["job_description"],
            ":f": user["follows"],
            ":a": user["is_all"],
            ":fn": user["first_name"],
            ":ln": user["last_name"],
            ":jt": user["item_title"],
            ":q": user["qualification"],
            ":ex": user["experience"],
            ":lc": user["user_location"],
            ":sk": user["skills"],
            ":d": datetime.utcnow().isoformat(),
        },
        ReturnValues="ALL_NEW",
    )
    return updated_job_alert["Attributes"]


def create_new_post(db, new_item):
    try:
        table = db.Table("posts")
        item = new_item
        item["id"] = str(uuid.uuid4())
        item["posted_date"] = datetime.utcnow().isoformat()
        item['sponsored'] = True
        item['source'] = 'diractly'
        item['url'] = "{}/post/{}".format(settings.base_url, item['id'])
        table.put_item(Item=item)
        return item
    except Exception as e:
        print(e)


def get_post_details_by_id(db, id):
    table = db.Table("posts")
    items = table.scan(FilterExpression=Key("id").eq(id))["Items"]
    if len(items) > 0:
        return items[0]
    return {}


def create_new_org(db, new_org):
    try:
        table = db.Table("organizations")
        org = table.scan(FilterExpression=Attr("email").eq(new_org['email']))[
            "Items"
        ]
        if org:
            org = org[0]
            if org.get("is_active"):
                return ValueError("email already exists")
            updated_org = table.update_item(
                Key={"id": org["id"]},
                UpdateExpression="set user_name = :u, organization = :o",
                ExpressionAttributeValues={
                    ":u": new_org['user_name'],
                    ":o": new_org['organization'],
                },
                ReturnValues="ALL_NEW",
            )["Attributes"]
            return updated_org

        _org = new_org
        _org["id"] = str(uuid.uuid4())
        _org["is_active"] = False
        _org["created_at"] = datetime.utcnow().isoformat()
        table.put_item(Item=_org)
        return _org
    except Exception as e:
        print(e)
        return {}


def get_org_by_id(db, org_id):
    table = db.Table("organizations")
    items = table.scan(FilterExpression=Key("id").eq(org_id))["Items"]
    if len(items) > 0:
        return items[0]
    return {}


def update_org_status(db, org_id, status=True):
    table = db.Table("organizations")
    table.update_item(
        Key={"id": org_id},
        UpdateExpression="set is_active = :r, modified_at =:d",
        ExpressionAttributeValues={":r": status, ":d": datetime.utcnow().isoformat()},
        ReturnValues="UPDATED_NEW",
    )


def get_org_by_email(db, email):
    table = db.Table("organizations")
    org = table.scan(FilterExpression=Attr("email").eq(email))["Items"]
    if len(org) > 0:
        return org[0]
    return {}
