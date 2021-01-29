"""
The first version of Sparrow's auth system was built on Flask-JWT-Extended.

- https://flask-jwt-extended.readthedocs.io/en/stable/
- https://github.com/vimalloc/flask-jwt-extended

This library is something of a monolith, and Starlette's session middleware
infrastructure provides a way to build something much cleaner and more sophisticated.

# Starlette authentication:

- https://www.starlette.io/authentication/

# Prior art:

- https://github.com/amitripshtos/starlette-jwt/tree/master/starlette_jwt [Uses headers]
- https://github.com/retnikt/star_jwt/blob/master/star_jwt/backend.py [Uses cookies]
- https://www.starlette.io/authentication/

# Context vars

- https://github.com/encode/starlette/issues/420

# A nice explanation of JWT:

- https://jwt.io/

# We store JWT tokens in cookies because it's more secure.
- https://flask-jwt-extended.readthedocs.io/en/latest/tokens_in_cookies.html

# However, we might want to include storing tokens API headers for programmatic access...

"""


# Implement authentication using JSON Web Tokens
# https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
# Authentication is managed on the browser using cookies
# to protect against XSS attacks.
# https://flask-jwt-extended.readthedocs.io/en/latest/tokens_in_cookies.html

# ORCID login
# https://members.orcid.org/api/integrate/orcid-sign-in

from os import environ
from starlette.authentication import AuthenticationError  # noqa
from starlette.middleware.authentication import AuthenticationMiddleware

from sparrow.plugins import SparrowCorePlugin
from .api import AuthAPI, get_backend  # noqa
from .backend import JWTBackend


class AuthPlugin(SparrowCorePlugin):
    name = "auth"

    backend = JWTBackend(environ.get("SPARROW_SECRET_KEY", ""))

    def on_asgi_setup(self, api):
        api.add_middleware(AuthenticationMiddleware, backend=self.backend)

    def on_api_initialized_v2(self, api):
        api.mount("/auth", AuthAPI, name="auth_api")
