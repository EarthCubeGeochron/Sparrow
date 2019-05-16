from os import environ
from datetime import timedelta
from pathlib import Path

LAB_NAME= environ.get("SPARROW_LAB_NAME", "Test lab")
DATABASE="postgresql:///earthcube_labdata_test"
BASE_URL= environ.get("SPARROW_BASE_URL", "/")

# We want to check most of our config into version control,
# but we should under no circumstances check in secret keys.
# Instead, we store it as an environment variable.
SECRET_KEY = environ.get("SPARROW_SECRET_KEY")
if SECRET_KEY is None:
    raise KeyError("Environment variable `SPARROW_SECRET_KEY` must be set")

# Schema extensions
sql = environ.get("SPARROW_INIT_SQL", None)
if sql is not None:
    p = Path(sql)
    assert p.exists()
    if p.is_dir():
        files = p.glob('*.sql')
    else:
        files = [p]
    INIT_SQL = [f for f in files if f.is_file()]

JWT_SECRET_KEY = SECRET_KEY
# We store JWT tokens in cookies because it's more secure.
# https://flask-jwt-extended.readthedocs.io/en/latest/tokens_in_cookies.html
JWT_TOKEN_LOCATION = ['cookies']

# Temporary, for development
JWT_COOKIE_CSRF_PROTECT = False
# We don't currently have the ACCESS/REFRESH token
# dynamic figured out, so we will set our access token
# expiration to 30 days
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)

# Only send access tokens to API endpoints
# Don't use `os.path.join` for urls as it does weird things with "absolute paths"
base = BASE_URL.rstrip('/')
JWT_ACCESS_COOKIE_PATH = f"{base}/api/v1"
JWT_REFRESH_COOKIE_PATH = f"{base}/api/v1/auth/refresh"
