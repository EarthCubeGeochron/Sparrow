"""
JSON Web Token authentication.

Prior art: https://github.com/retnikt/star_jwt/blob/master/star_jwt/backend.py
"""
import time
from typing import (
    Tuple,
    Dict,
    Optional,
    Set,
    Sequence,
    TypeVar,
    Any,
    Mapping,
    Type,
)

import jwt
from starlette.authentication import (
    BaseUser,
    AuthenticationBackend,
    AuthCredentials,
    AuthenticationError,
    UnauthenticatedUser,
)
from starlette.requests import Request
from starlette.responses import Response
from sparrow.logs import get_logger

log = get_logger(__name__)


class JWTBackend(AuthenticationBackend):
    def __init__(
        self,
        encode_key: str,
        *,
        decode_key: Optional[str] = None,
        json_encoder: Optional[Type] = None,
        anonymous_scopes: Sequence[str] = (),
        default_algorithm: str = "HS256",
        algorithms: Optional[Set[str]] = frozenset(),
        options: Dict = None,
        headers: Optional[Mapping] = None,
        issuer: str = None,
        audience: str = None,
        add_iat: bool = True,
        add_nbf: bool = True,
        max_age: Optional[int] = None,
        cookie_name: str = "auth",
        path: str = "/",
        secure: bool = False,
        http_only: bool = True,
        domain: Optional[str] = None,
        **kwargs: Any,
    ):
        """
        JSON Web Token authenticator backend for Starlette's authentication system.
        Example usage::
            from starlette.applications import Starlette
            from starlette.middleware.authentication import AuthenticationMiddleware
            from star_jwt import JWTBackend
            app = Starlette()
            backend = JWTBackend(...)
            app.add_middleware(AuthenticationMiddleware, backend=backend)
        :param Type json_encoder: class to encode JSON with
        :param Sequence[str] anonymous_scopes: list of scopes to grant to unauthenticated users only
        :param str cookie_name: name of the login cookie
        :param str path: path of the login cookie - https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#Scope_of_cookies
        :param bool secure: whether the login cookie requires HTTPS - https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#Secure_and_HttpOnly_cookies
        :param bool http_only: whether the login cookie should be inaccessible from
        javascript - https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#Secure_and_HttpOnly_cookies
        :param int max_age: how long the cookie and token should last, in seconds
        :param str domain: domain for the cookie to work on - https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#Scope_of_cookies
        :param str encode_key: key to encode JWTs with
        :param Optional[str] decode_key: key to decode JWTs with. Same as encode_key by default, useful only with
        asymmetric algorithms
        :param str default_algorithm: algorithm to use for encoding
        :param Sequence[str] algorithms: algorithms to allow for decoding
        :param Mapping options: options to pass to JWT decode
        :param str issuer: issuer to add to JWT
        :param str audience: audience to add to JWT
        :param bool add_iat: whether to add the time of issue to JWT
        :param bool add_nbf: whether to add a not-before field to the JWT
        :param Mapping headers: additional headers to add to the JWT
        :param Any kwargs: kwargs to pass to JWT decode
        """
        self.json_encoder = json_encoder
        self.anonymous_scopes = anonymous_scopes
        self.cookie_name = cookie_name
        self.path = path
        self.secure = secure
        self.http_only = http_only
        self.max_age = max_age
        self.domain = domain
        self.encode_key = encode_key
        self.decode_key = decode_key or self.encode_key
        self.default_algorithm = default_algorithm
        self.algorithms = list(algorithms | {default_algorithm})
        self.options = options
        self.issuer = issuer
        self.audience = audience
        self.add_iat = add_iat
        self.add_nbf = add_nbf
        self.headers = headers
        self.kwargs = kwargs

    async def get_user(
        self, request: Request, /, **kwargs
    ) -> Tuple[AuthCredentials, BaseUser]:
        """
        override this method to get your user from the database, for example.
        By default this returns an empty user with only the user
        :param request: the Starlette request
        :param kwargs: content of the JWT
        :return: tuple of (credentials object, user object)
        """
        log.debug(kwargs)
        raise NotImplementedError()

    async def authenticate(self, request: Request) -> Tuple[AuthCredentials, BaseUser]:
        """
        gets the user for the request
        """
        if (cookie := request.cookies.get(self.cookie_name)) is None:
            return AuthCredentials(self.anonymous_scopes), UnauthenticatedUser()

        try:
            value = jwt.decode(
                cookie,
                key=self.decode_key,
                verify=True,
                algorithms={"HS256"},
                options=self.options,
                issuer=self.issuer,
                audience=self.audience,
                **self.kwargs,
            )
        except jwt.PyJWTError as e:
            raise AuthenticationError(*e.args) from None

        return await self.get_user(request, **value)

    response = TypeVar("response", bound=Response)

    def set_login_cookie(self, response: response, /, **data: Any) -> response:
        """
        sets a login cookie on a given Response
        :param response: response to set the cookie on
        :param data: token payload data, overrides built-in fields (iat, nbf, iss, aud, exp, etc...)
        :return: the response, useful for chaining
        """

        payload = {}

        now = time.time()
        if self.add_iat:
            payload.update(iat=now)
        if self.add_nbf:
            payload.update(nbf=now)
        if self.max_age is not None:
            payload.update(exp=now + self.max_age)

        if self.audience is not None:
            payload.update(aud=self.audience)
        if self.issuer is not None:
            payload.update(iss=self.issuer)

        payload.update(data)

        encoded = jwt.encode(
            payload,
            key=self.encode_key,
            algorithm="HS256",
            headers=self.headers,
            json_encoder=self.json_encoder,
        ).decode()

        response.set_cookie(
            self.cookie_name,
            value=encoded,
            max_age=self.max_age,
            path=self.path,
            secure=self.secure,
            httponly=self.http_only,
            domain=self.domain,
        )

        return response

    def logout(self, response: response) -> response:
        """
        deletes the login cookie. Note that if you have set data on the
        session (using itsdangerous / Starlette's SessionMiddleware), it will
        need to be cleared separately.
        :param response: response on which to delete the cookie
        :return: the response, useful for chaining
        """
        response.delete_cookie(key=self.cookie_name, path=self.path, domain=self.domain)
        return response
