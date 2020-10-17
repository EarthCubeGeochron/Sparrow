"""
The first version of Sparrow's auth system was built on Flask-JWT-Extended.

- https://flask-jwt-extended.readthedocs.io/en/stable/
- https://github.com/vimalloc/flask-jwt-extended

This library is something of a monolith, and Starlette's session middleware
infrastructure provides a way to build something much cleaner and more sophisticated.

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

from contextvars import ContextVar
from uuid import uuid4

# ContextVar is an extremely shiny built-in Python 3.7 feature
# It should allow us to build a globally accessible auth system
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request


REQUEST_ID_CTX_KEY = "request_id"

_request_id_ctx_var: ContextVar[str] = ContextVar(REQUEST_ID_CTX_KEY, default=None)


def get_request_id() -> str:
    return _request_id_ctx_var.get()


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        request_id = _request_id_ctx_var.set(str(uuid4()))

        response = await call_next(request)

        _request_id_ctx_var.reset(request_id)

        return response
