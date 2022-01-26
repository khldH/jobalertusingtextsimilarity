from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    aws_region_name: Optional[str]
    aws_access_key_id: Optional[str]
    aws_secret_access_key: Optional[str]
    host = "localhost"
    port = 8001
    mail_sender: str
    mail_sender_password: str
    smtp_server: str
    secret_key = "HS1XYZ"
    token_algorithm = "HS256"
    registration_token_lifetime = 60 * 60
    base_url = "{}:{}".format(host, str(port))

    class Config:
        env_file = ".env"


settings = Settings()
