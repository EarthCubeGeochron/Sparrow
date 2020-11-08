from os import environ

LAB_NAME = environ.get("SPARROW_LAB_NAME", "Test lab")
DATABASE = environ.get("SPARROW_DATABASE", "postgresql+psycopg2:///sparrow")
BASE_URL = environ.get("SPARROW_BASE_URL", "/")

# We want to check most of our config into version control,
# but we should under no circumstances check in secret keys.
# Instead, we store it as an environment variable.
SECRET_KEY = environ.get("SPARROW_SECRET_KEY")
if SECRET_KEY is None:
    raise KeyError("Environment variable `SPARROW_SECRET_KEY` must be set")
