from flask import Blueprint

web = Blueprint('frontend', __name__)

@web.route('/')
def index():
    return "Hello, world from lab data land!"
