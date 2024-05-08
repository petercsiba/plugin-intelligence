import os

from dotenv import load_dotenv

load_dotenv()


ENV = os.environ.get("ENV")
ENV_LOCAL = "local"
ENV_TEST = "test"
ENV_PROD = "prod"

OPEN_AI_API_KEY = os.environ.get("OPEN_AI_API_KEY")

POSTGRES_DATABASE_URL = os.environ.get("POSTGRES_DATABASE_URL")
