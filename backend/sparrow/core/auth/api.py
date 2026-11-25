from starlette.authentication import AuthenticationError, requires
from starlette.responses import JSONResponse
from starlette.routing import Route, Router

from sparrow.core.context import get_database, get_sparrow_app
from sparrow.database.models import User
from sparrow.logs import get_logger

from .orcid import orcid_callback, orcid_login, orcid_status

log = get_logger(__name__)


def get_backend():
    app = get_sparrow_app()
    return app.plugins.get("auth").backend


def UnauthorizedResponse(orcid=None, **kwargs):
    data = dict(login=False, username=None, message="user is not authenticated")
    if orcid is not None:
        data["orcid"] = orcid
    return JSONResponse(data, **kwargs)


async def login(request):
    try:
        data = await request.json()
    except ValueError:
        data = None
    if not isinstance(data, dict):
        data = {}
    username = data.get("username")
    password = data.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return JSONResponse(
            {"error": "Provide a username and a password"}, status_code=422
        )
    db = get_database()
    backend = get_backend()

    current_user = db.session.query(User).get(username)
    log.debug(current_user)

    if current_user is not None and current_user.is_correct_password(password):
        day = 24 * 60 * 60
        token = backend.set_cookie(
            None, "access", max_age=day, identity=username, role="admin"
        )
        resp = JSONResponse(dict(login=True, username=username, token=token))
        return backend.set_login_cookies(resp, identity=username)

    return backend.logout(UnauthorizedResponse(status_code=401))


def logout(request):
    backend = get_backend()
    return backend.logout(UnauthorizedResponse(status_code=200))


def status(request):
    backend = get_backend()
    orcid = orcid_status(request)
    try:
        identity = backend.get_identity(request)
        return JSONResponse(dict(login=True, username=identity, orcid=orcid))
    except AuthenticationError:
        # We have to handle authentication errors to return a 200 response
        # even though the user is logged out
        return UnauthorizedResponse(status_code=200, orcid=orcid)


def refresh(request):
    # JWT refresh token required
    backend = get_backend()
    identity = backend.get_identity(request, type="refresh")
    response = JSONResponse(dict(login=True, refresh=True, username=identity))

    return backend.set_access_cookie(response, identity=identity, role="admin")


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
        Route("/orcid/login", endpoint=orcid_login),
        Route("/orcid/callback", endpoint=orcid_callback),
    ]
)
