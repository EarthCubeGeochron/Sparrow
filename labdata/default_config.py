from os import environ

LAB_NAME="Test lab"
DATABASE="postgresql:///earthcube_labdata_test"

# We want to check most of our config into version control,
# but we should under no circumstances check in secret keys.
# Instead, we store it as an environment variable.
SECRET_KEY = environ.get("LABDATA_SECRET_KEY")
if SECRET_KEY is None:
    raise KeyError("Environment variable `LABDATA_SECRET_KEY` must be set")

JWT_SECRET_KEY = SECRET_KEY

# We store JWT tokens in cookies because it's more secure.
# https://flask-jwt-extended.readthedocs.io/en/latest/tokens_in_cookies.html
JWT_TOKEN_LOCATION = ['cookies']
# Only send access tokens to API endpoints
JWT_ACCESS_COOKIE_PATH = '/api/v1'

JWT_REFRESH_COOKIE_PATH = '/api/v1/auth/refresh'
