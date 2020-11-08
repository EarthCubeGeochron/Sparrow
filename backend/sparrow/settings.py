from starlette.config import Config

config = Config()

LAB_NAME = config("SPARROW_LAB_NAME", "Test lab")
DATABASE = config("SPARROW_DATABASE", "postgresql+psycopg2:///sparrow")
BASE_URL = config("SPARROW_BASE_URL", "/")

SECRET_KEY = config("SPARROW_SECRET_KEY", None)
if SECRET_KEY is None:
    raise KeyError("Environment variable `SPARROW_SECRET_KEY` must be set")
