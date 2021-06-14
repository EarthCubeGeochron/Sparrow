"""
An API for managing users
"""
from starlette.routing import Route, Router
from sparrow.plugins import SparrowCorePlugin
from sparrow.database.models import User
from sparrow.api import APIResponse, SparrowAPIError
from sparrow.context import get_database
from sparrow.auth.create_user import _create_user
from sparrow.logs import get_logger

log = get_logger(__name__)


def validate_password(password):
    if len(password) < 4:
        raise SparrowAPIError("Password is too short")
    return password


async def user(request):
    db = get_database()
    user_id = request.path_params["user_id"]
    UserSchema = db.interface.user
    _schema = UserSchema(many=False, exclude=("password",))
    with db.session_scope(commit=False):
        user = db.session.query(User).get(user_id)
        if request.method == "GET":
            return APIResponse(user, schema=_schema)
        elif request.method == "PUT":
            # Update an existing user
            data = await request.json()
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
            return APIResponse(user, schema=_schema)

        elif request.method == "DELETE":
            user.delete()
            db.session.commit()
            return APIResponse({"success": True, "deleted": [user_id]})


async def create_user(db, User, request):
    db = get_database()
    User = db.model.user
    UserSchema = db.interface.user
    res = await request.json()
    try:
        username = res["username"]
        password = res["password"]
    except IndexError:
        raise SparrowAPIError("Must provide both username and password")
    if UserSchema.query(db.session).get(username) is not None:
        raise SparrowAPIError(f"User {username} already exists", 409)
    res = _create_user(db, username, validate_password(password))
    return APIResponse(res, schema=UserSchema(many=False, exclude=("password",)))


async def users(request):
    db = get_database()
    User = db.model.user
    UserSchema = db.interface.user
    with db.session_scope(commit=False):
        if request.method == "POST":
            return create_user(db, UserSchema, request)

        res = db.session.query(User).all()
        return APIResponse(res, schema=UserSchema(many=True, exclude=("password",)))


UserAPI = Router(
    [
        Route("/{user_id}", endpoint=user),
        Route("/", endpoint=users, methods=["GET", "POST"]),
    ]
)


class UserManagementPlugin(SparrowCorePlugin):
    name = "user-management"

    def on_api_initialized_v2(self, api):
        api.mount("/users", UserAPI, name="auth")
