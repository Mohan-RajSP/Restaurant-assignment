import os
from dotenv import load_dotenv, find_dotenv
import datetime

load_dotenv(find_dotenv())

class Config:
    """Set Flask configuration vars from .env file."""

    # General Config
    SECRET_KEY = os.getenv('SECRET_KEY')
    FLASK_ENV = os.getenv('FLASK_ENV')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG')

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')

    GITLAB_OAUTH_CLIENT_ID= os.getenv("CLIENT_ID")
    GITLAB_OAUTH_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    OAUTHLIB_RELAX_TOKEN_SCOPE = "1"
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=24)


