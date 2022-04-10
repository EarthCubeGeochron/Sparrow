from starlette.config import Config

config = Config()

LAB_NAME = config("SPARROW_LAB_NAME", default="Test lab")
DATABASE = config("SPARROW_DATABASE", default="postgresql+psycopg2:///sparrow")
BASE_URL = config("SPARROW_BASE_URL", default="/")
ECHO_SQL = config("SPARROW_ECHO_SQL", cast=bool, default=False)
DATA_DIR = config("SPARROW_DATA_DIR", default="/data")
CACHE_DIR = config("SPARROW_CACHE_DIR", default="/cache")
TASK_BROKER = config("SPARROW_TASK_BROKER", default=None)
TASK_WORKER_ENABLED = config("SPARROW_TASK_WORKER", cast=bool, default=True)

SECRET_KEY = config("SPARROW_SECRET_KEY", None)
if SECRET_KEY is None:
    raise KeyError("Environment variable `SPARROW_SECRET_KEY` must be set")
