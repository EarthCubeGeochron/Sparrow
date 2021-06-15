"""
An API for managing users
"""
from starlette.routing import Route, Router
from starlette.authentication import requires
from sparrow.plugins import SparrowCorePlugin
from sparrow.database.models import User
from sparrow.api import APIResponse, SparrowAPIError
from sparrow.context import get_database
from sparrow.auth import get_backend
from sparrow.auth.create_user import _create_user
from sparrow.logs import get_logger
from collections.abc import Iterable

log = get_logger(__name__)


def validate_password(password):
    if len(password) < 4:
        raise SparrowAPIError("Password is too short")
    return password


class UserResponse(APIResponse):
    def __init__(self, user_):
        db = get_database()
        _many = isinstance(user_, Iterable)
        _schema = db.interface.user(many=_many, exclude=("password",))
        super().__init__(user_, schema=_schema)


def update_user(db, user, data):
    # Update an existing user
    password = data.get("password", None)
    if password is not None:
        user.set_password(validate_password(password))

    # We could probably use schemas nicely here, but we do things manually for now
    for field in ("username", "researcher"):
        try:
            setattr(user, field=data.get(field))
        except KeyError:
            pass
    db.session.add(user)
    db.session.commit()
    return UserResponse(user)


@requires("admin")
async def user(request):
    auth = get_backend()
    db = get_database()
    username = request.path_params["username"]
    with db.session_scope(commit=False):
        user = db.session.query(User).get(username)
        if user is None:
            raise SparrowAPIError("User {username} does not exist", 404)
        if request.method == "GET":
            return UserResponse(user)
        elif request.method == "PUT":
            data = await request.json()
            return update_user(db, user, data)
        elif request.method == "DELETE":
            # Make sure we aren't trying to delete ourselves
            if user.username == auth.get_identity(request):
                raise SparrowAPIError("Cannot delete yourself", 403)
            user.delete()
            db.session.commit()
            return APIResponse({"success": True, "deleted": [username]})
        raise SparrowAPIError("Method not allowed", 405)


async def create_user(db, data):
    db = get_database()
    try:
        username = data["username"]
        password = data["password"]
    except IndexError:
        raise SparrowAPIError("Must provide both username and password")
    if db.session.query(User).get(username) is not None:
        raise SparrowAPIError(f"User {username} already exists", 409)
    res = _create_user(db, username, validate_password(password))
    return UserResponse(res)


@requires("admin")
async def users(request):
    db = get_database()
    User = db.model.user
    with db.session_scope(commit=False):
        if request.method == "POST":
            data = await request.json()
            return create_user(db, data)

        res = db.session.query(User).all()
        return UserResponse(res)


UserAPI = Router(
    [
        Route("/{username}", endpoint=user, methods=["GET", "PUT", "DELETE"]),
        Route("/", endpoint=users, methods=["GET", "POST"]),
    ]
)


class UserManagementPlugin(SparrowCorePlugin):
    name = "user-management"

    def on_api_initialized_v2(self, api):
        api.mount("/users", UserAPI, name="auth")
