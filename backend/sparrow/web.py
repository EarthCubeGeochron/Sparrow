from flask import Blueprint, render_template, current_app
from os.path import join

web = Blueprint('frontend', __name__)

@web.route('/')
# This route is a catch-all route for anything
# beneath the / endpoint. Allows
# the API explorer to function with client-side
# routing with react-router...
@web.route('/<path:path>')
def index(path='/'):
    v = current_app.config.get("LAB_NAME")
    base_url = current_app.config.get("BASE_URL")
    return render_template('page.html',
            title=v,
            id='index',
            asset_dir=join(base_url, 'assets'))
