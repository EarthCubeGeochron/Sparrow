"""
JSON Web Token authentication.

"""
import time
from typing import Tuple, Any

import jwt
import warnings
from starlette.authentication import (
    BaseUser,
    SimpleUser,
    AuthenticationBackend,
    AuthCredentials,
    AuthenticationError,
    UnauthenticatedUser,
)
from starlette.requests import Request
from starlette.responses import Response
from sparrow.logs import get_logger

log = get_logger(__name__)

hour = 60 * 60
day = 24 * hour
month = 30 * day


class JWTBackend(AuthenticationBackend):
    """JSON Web Token authenticator backend for Starlette's authentication system.

    Prior art: https://github.com/retnikt/star_jwt/blob/master/star_jwt/backend.py

    Creates two cookies: `access_token_cookie` and `refresh_token_cookie`. This
    structure is modeled on `flask_jwt_extended`. Each cookie should have a `type`
    and `identity` field.
    """

    def __init__(self, encode_key: str):
        self.encode_key = encode_key

    def set_cookie(self, response: Response, type, **data):
        """set a basic cookie on the response"""
        now = time.time()
        # Cookies last for a day by default
        max_age = data.pop("max_age", day)
        name = type + "_token_cookie"

        payload = dict(iat=now, nbf=now, exp=now + max_age, type=type)
        payload.update(data)

        token = self._encode(payload).decode("utf-8")

        if response is None:
            return token

        response.set_cookie(
            name,
            value=token,
            max_age=max_age,
            # We could set this to make cookies valid only at secure paths
            secure=False,
            httponly=False,
            # Could set domain and path here...
        )

    def _encode(self, payload, **kwargs):
        kwargs.update(key=self.encode_key, algorithm="HS256")
        return jwt.encode(payload, **kwargs)

    def _decode(self, cookie, **kwargs):
        kwargs.update(key=self.encode_key, verify=True, algorithms={"HS256"})
        return jwt.decode(
            cookie,
            # do symmetrical encryption for now
            **kwargs,
        )

    def get_identity(self, request: Request, type="access"):
        name = f"{type}_token_cookie"
        try:
            cookie = request.cookies.get(name)
            if cookie is None:
                if "Authorization" not in request.headers:
                    raise AuthenticationError(f"Could not find {name} on request")
                else:
                    header = request.headers["Authorization"]
                    if header.startswith("Bearer "):
                        header = header[7:]
                    else:
                        warnings.warn(
                            "Authorization header did not start with 'Bearer '. This is invalid and deprecated."
                        )
                    value = self._decode(header)
            else:
                value = self._decode(cookie)

            identity = value.get("identity")
            if identity is None:
                raise AuthenticationError(f"{name} has no key identity")
            if type != value.get("type"):
                raise AuthenticationError(f"{name} did not have a matching type")
            return identity
        except jwt.PyJWTError as e:
            raise AuthenticationError(*e.args) from None

    async def authenticate(self, request: Request) -> Tuple[AuthCredentials, BaseUser]:
        try:
            identity = self.get_identity(request, type="access")
            log.info(f"Authenticating with {identity}")
            # We could check that we actually have a valid user here, but this doesn't
            # seem to be what other libraries tend to do.
            user = SimpleUser(identity)
            return (AuthCredentials(("admin",)), user)
        except AuthenticationError as err:
            return (AuthCredentials(("public",)), UnauthenticatedUser())

    def set_login_cookies(self, response: Response, **data: Any) -> Response:
        self.set_access_cookie(response, **data)
        self.set_cookie(response, "refresh", max_age=month, **data)
        return response

    def set_access_cookie(self, response: Response, **data: Any) -> Response:
        self.set_cookie(response, "access", max_age=day, **data)
        return response

    def logout(self, response: Response) -> Response:
        response.delete_cookie(key="access_token_cookie")
        response.delete_cookie(key="refresh_token_cookie")
        return response
