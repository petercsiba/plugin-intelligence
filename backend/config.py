import os

from dotenv import load_dotenv

load_dotenv()


ENV = os.environ.get("ENV")
ENV_LOCAL = "local"
ENV_TEST = "test"
ENV_PROD = "prod"

POSTGRES_DATABASE_URL = os.environ.get("POSTGRES_DATABASE_URL")
