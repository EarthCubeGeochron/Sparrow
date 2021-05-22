from starlette.routing import Route, Router
from starlette.responses import JSONResponse
from starlette.authentication import requires, AuthenticationError
from webargs_starlette import use_annotations
from sparrow.database.models import User
from sparrow.context import get_sparrow_app, get_database
from sparrow.logs import get_logger

log = get_logger(__name__)


def get_backend():
    app = get_sparrow_app()
    return app.plugins.get("auth").backend


def UnauthorizedResponse(**kwargs):
    return JSONResponse(dict(login=False, username=None, message="user is not authenticated"), **kwargs)


@use_annotations(location="json")
async def login(request, username: str, password: str):
    db = get_database()
    backend = get_backend()

    current_user = db.session.query(User).get(username)
    log.debug(current_user)

    if current_user is not None and current_user.is_correct_password(password):
        day = 24 * 60 * 60
        token = backend.set_cookie(None, "access", max_age=day,identity=username)
        resp = JSONResponse(dict(login=True, username=username, token=token))
        return backend.set_login_cookies(resp, identity=username)

    return backend.logout(UnauthorizedResponse(status_code=401))


def logout(request):
    backend = get_backend()
    return backend.logout(UnauthorizedResponse(status_code=200))


def status(request):
    backend = get_backend()
    try:
        identity = backend.get_identity(request)
        return JSONResponse(dict(login=True, username=identity))
    except AuthenticationError:
        # We have to handle authentication errors to return a 200 response
        # even though the user is logged out
        return UnauthorizedResponse(status_code=200)


def refresh(request):
    # JWT refresh token required
    backend = get_backend()
    identity = backend.get_identity(request, type="refresh")
    response = JSONResponse(dict(login=True, refresh=True, username=identity))

    return backend.set_access_cookie(response, identity=identity)


@requires("admin")
def secret(request):
    # JWT required
    return JSONResponse({"answer": 42})


AuthAPI = Router(
    [
        Route("/login", endpoint=login, methods=["POST"]),
        Route("/logout", endpoint=logout, methods=["POST"]),
        Route("/refresh", endpoint=refresh, methods=["POST"]),
        Route("/status", endpoint=status),
        Route("/secret", endpoint=secret),
    ]
)
