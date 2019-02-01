# Implement authentication using JSON Web Tokens
# https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb

# ORCID login
# https://members.orcid.org/api/integrate/orcid-sign-in

from flask import current_app
from flask_restful import Resource, reqparse
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)
from ..api.base import APIResourceCollection
from ..models import User

parser = reqparse.RequestParser()
parser.add_argument('username',
    help='This field cannot be blank',
    required=True)
parser.add_argument('password',
    help='This field cannot be blank',
    required=True)

AuthAPI = APIResourceCollection()

@AuthAPI.resource('/registration')
class UserRegistration(Resource):
    def post(self):
        # This route is a skeleton right now
        raise NotImplementedError()

def user_login(self):
    db = current_app.database
    data = parser.parse_args()
    username = data['username']
    password = data['password']

    current_user = db.session.query(User).get(username)
    if current_user is None:
        return dict(message= f"User {username} doesn't exist")

    if current_user.is_correct_password(password):
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        return dict(
            message=f"Logged in as {current_user.username}",
            access_token=access_token,
            refresh_token=refresh_token)
    else:
        return dict(message='Wrong credentials')

@AuthAPI.resource('/login')
class UserLogin(Resource):
    post = user_login

@AuthAPI.resource('/token/refresh')
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return dict(access_token=access_token)

@AuthAPI.resource('/secret')
class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {'answer': 42}
