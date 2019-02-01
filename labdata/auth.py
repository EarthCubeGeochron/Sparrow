# Implement authentication using JSON Web Tokens
# https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb

from flask_restful import Resource
from .api.base import APIResourceCollection

AuthAPI = APIResourceCollection()

@AuthAPI.resource('/registration')
class UserRegistration(Resource):
    def post(self):
        return {'message': 'User registration'}

@AuthAPI.resource('/login')
class UserLogin(Resource):
    def post(self):
        return {'message': 'User login'}

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
