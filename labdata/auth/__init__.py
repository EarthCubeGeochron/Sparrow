# Implement authentication using JSON Web Tokens
# https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb

# ORCID login
# https://members.orcid.org/api/integrate/orcid-sign-in

from flask_restful import Resource, reqparse
from ..api.base import APIResourceCollection

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
        data = parser.parse_args()
        return data

@AuthAPI.resource('/login')
class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        return data

@AuthAPI.resource('/logout/access')
class UserLogoutAccess(Resource):
    def post(self):
        return {'message': 'User logout'}

@AuthAPI.resource('/logout/refresh')
class UserLogoutRefresh(Resource):
    def post(self):
        return {'message': 'User logout'}

@AuthAPI.resource('/token/refresh')
class TokenRefresh(Resource):
    def post(self):
        return {'message': 'Token refresh'}

@AuthAPI.resource('/users')
class AllUsers(Resource):
    def get(self):
        return {'message': 'List of users'}

    def delete(self):
        return {'message': 'Delete all users'}

@AuthAPI.resource('/secret')
class SecretResource(Resource):
    def get(self):
        return {'answer': 42}
