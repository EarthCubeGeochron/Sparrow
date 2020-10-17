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

from flask import current_app, jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    jwt_optional,
    get_jwt_identity,
)
from ..api.v1.base import APIResourceCollection
from ..database.models import User
from ..plugins import SparrowCorePlugin
from .api import get_backend
from jwt.exceptions import InvalidSignatureError
from starlette.authentication import AuthenticationError

parser = reqparse.RequestParser()
parser.add_argument("username", help="This field cannot be blank", required=True)
parser.add_argument("password", help="This field cannot be blank", required=True)

AuthAPI = APIResourceCollection()


@AuthAPI.resource("/registration")
class UserRegistration(Resource):
    def post(self):
        # This route is a skeleton right now
        raise NotImplementedError()


def user_login(self):
    db = current_app.database
    data = parser.parse_args()
    print(data)
    username = data["username"]
    password = data["password"]

    current_user = db.session.query(User).get(username)
    if current_user is None:
        resp = jsonify(login=False, username=None)
        unset_jwt_cookies(resp)
        return resp

    if not current_user.is_correct_password(password):
        resp = jsonify(login=False, username=username)
        unset_jwt_cookies(resp)
        return resp

    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)

    resp = jsonify(login=True, username=username)
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp


@AuthAPI.resource("/login")
class Login(Resource):
    post = user_login


@AuthAPI.resource("/logout")
class Logout(Resource):
    def post(self):
        resp = jsonify({"login": False})
        unset_jwt_cookies(resp)
        return resp


@AuthAPI.resource("/status")
class Status(Resource):
    @jwt_optional
    def get(self):
        username = get_jwt_identity()
        if username:
            resp = jsonify(login=True, username=username)
            return resp
        return jsonify(login=False)


@AuthAPI.resource("/refresh")
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        username = get_jwt_identity()
        access_token = create_access_token(identity=username)
        resp = jsonify(login=True, refresh=True, username=username)
        set_access_cookies(resp, access_token)
        return resp


@AuthAPI.resource("/secret")
class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {"answer": 42}


class AuthPlugin(SparrowCorePlugin):
    name = "auth"

    def on_database_ready(self, db):
        # Manage JSON Web tokens
        JWTManager(self.app)

    def on_api_initialized(self, api):
        api.add_resource(AuthAPI, "/auth")
