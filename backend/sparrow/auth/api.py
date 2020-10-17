from sparrow.api.response import APIResponse
from sparrow.plugins import SparrowCorePlugin
from starlette.routing import Route, Router
from starlette.middleware.authentication import AuthenticationMiddleware
from os import environ
from .backend import JWTBackend
from webargs_starlette import use_annotations
from sparrow.database.models import User
from sparrow.context import app_context
from sparrow.logs import get_logger

log = get_logger(__name__)


@use_annotations(location="json")
def login(request, username: str, password: str):
    ctx = app_context()
    db = ctx.database
    backend = ctx.plugins.get("auth-v2").backend

    current_user = db.session.query(User).get(username)
    log.debug(current_user)

    if current_user is None:
        response = APIResponse(dict(login=False, username=None))
        return response  # backend.logout(response)

    if not current_user.is_correct_password(password):
        response = APIResponse(dict(login=False, username=username))
        return response  # backend.logout(response)

    # access_token = create_access_token(identity=username)
    # refresh_token = create_refresh_token(identity=username)

    resp = APIResponse(dict(login=True, username=username))
    return resp  # backend.set_login_cookie(resp)

    # set_access_cookies(resp, access_token)
    # set_refresh_cookies(resp, refresh_token)
    # return resp


def logout(request):
    return APIResponse(dict(login=False))


def status(request):
    username = None
    # get_jwt_identity()
    if username:
        resp = APIResponse(dict(login=True, username=username))
        return resp
    return APIResponse(dict(login=False))


def refresh(request):
    # JWT refresh token required
    username = None  # get_jwt_identity()
    # access_token = create_access_token(identity=username)
    resp = APIResponse(dict(login=True, refresh=True, username=username))
    # set_access_cookies(resp, access_token)
    return resp


def secret(request):
    # JWT required
    return APIResponse({"answer": 42})


routes = [
    Route("/login", endpoint=login, methods=["POST"]),
    Route("/logout", endpoint=logout, methods=["POST"]),
    Route("/refresh", endpoint=refresh, methods=["POST"]),
    Route("/status", endpoint=status),
    Route("/secret", endpoint=secret),
]


class AuthV2Plugin(SparrowCorePlugin):
    name = "auth-v2"

    backend = JWTBackend(encode_key=environ.get("SPARROW_SECRET_KEY", ""))

    def on_asgi_setup(self, api):
        api.add_middleware(AuthenticationMiddleware, backend=self.backend)

    def on_api_initialized_v2(self, api):
        api.mount("/auth", Router(routes))
