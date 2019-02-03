# Implement authentication using JSON Web Tokens
# https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
# Authentication is managed on the browser using cookies
# to protect against XSS attacks.
# https://flask-jwt-extended.readthedocs.io/en/latest/tokens_in_cookies.html

# ORCID login
# https://members.orcid.org/api/integrate/orcid-sign-in

from flask import current_app, jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                set_access_cookies, set_refresh_cookies,
                                unset_jwt_cookies,
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

@AuthAPI.resource('/login')
class Login(Resource):
    post = user_login

@AuthAPI.resource('/logout')
class Logout(Resource):
    def post(self):
        resp = jsonify({'logout': True})
        unset_jwt_cookies(resp)
        return resp

@AuthAPI.resource('/status')
class Status(Resource):
    @jwt_required
    def get(self):
        username = get_jwt_identity()
        resp = jsonify(login=True, username=username)
        return resp

@AuthAPI.resource('/refresh')
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        username = get_jwt_identity()
        access_token = create_access_token(identity=username)
        resp = jsonify(refresh=True, username=username)
        set_access_cookies(resp)
        return resp

@AuthAPI.resource('/secret')
class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {'answer': 42}
