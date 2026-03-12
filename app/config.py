import os
from datetime import timedelta
from urllib.parse import quote_plus

from dotenv import load_dotenv


load_dotenv()


def resolve_database_uri():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url

    mysql_host = os.getenv("MYSQL_HOST")
    if mysql_host:
        mysql_user = os.getenv("MYSQL_USER", "root")
        mysql_password = quote_plus(os.getenv("MYSQL_PASSWORD", ""))
        mysql_port = os.getenv("MYSQL_PORT", "3306")
        mysql_db = os.getenv("MYSQL_DB", "blogpersonnel")
        return (
            f"mysql+pymysql://{mysql_user}:{mysql_password}"
            f"@{mysql_host}:{mysql_port}/{mysql_db}?charset=utf8mb4"
        )

    return "sqlite:///blog.db"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = resolve_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
