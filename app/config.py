from typing import Optional

import boto3
from pydantic import BaseSettings


class Settings(BaseSettings):
    # database_hostname: str
    # database_port: str
    # database_password: str
    # database_name: str
    # database_username: str
    aws_region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    endpoint_url: str = None
    host = "localhost"
    port = 8080
    mail_sender: str
    mail_sender_password: str
    smtp_server: str
    secret_key = "HS1XYZ"
    token_algorithm = "HS256"
    registration_token_lifetime = 60 * 60
    base_url = "{}:{}".format(host, str(port))
    is_prod: bool

    class Config:
        env_file = ".env"


settings = Settings()
