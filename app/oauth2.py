import uuid
from datetime import datetime, timedelta

from jose import jwt
from pydantic import UUID4

from .config import settings


class Auth:
    @staticmethod
    def get_token(data: dict, expires_delta: int):
        to_encode = data.copy()
        to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=expires_delta)})
        return jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.token_algorithm
        )

    @staticmethod
    def get_confirmation_token(user_id: UUID4):
        jti = str(uuid.uuid4())
        claims = {"sub": str(user_id), "scope": "registration", "jti": jti}
        return {
            "jti": jti,
            "token": Auth.get_token(claims, settings.registration_token_lifetime),
        }
