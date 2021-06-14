"""
An API for managing users
"""
from starlette.routing import Route, Router
from starlette.exceptions import HTTPException
from sparrow.plugins import SparrowCorePlugin
from sparrow.api import APIResponse
from sparrow.context import get_database
from sparrow.auth.create_user import _create_user
from sparrow.logs import get_logger

log = get_logger(__name__)


async def user(request):
    db = get_database()
    user_id = request.path_params["user_id"]
    User = db.model.user
    UserSchema = db.interface.user
    obj = db.session.query(User).get(user_id)

    if request.method == "GET":
        return APIResponse(obj, schema=UserSchema(many=False, exclude=("password",)))


async def create_user(db, User, request):
    db = get_database()
    User = db.model.user
    UserSchema = db.interface.user
    res = await request.json()
    try:
        username = res["username"]
        password = res["password"]
    except IndexError:
        return HTTPException(400, "Must provide both username and password")
    if UserSchema.query(db.session).get(username) is not None:
        return HTTPException(409, f"User {username} already exists")
    if len(password) < 4:
        return HTTPException(400, f"Password is too short")
    res = _create_user(db, username, password)
    return APIResponse(res, schema=UserSchema(many=False, exclude=("password",)))


async def users(request):
    db = get_database()
    User = db.model.user
    UserSchema = db.interface.user
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
