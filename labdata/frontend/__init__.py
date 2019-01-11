from flask import Blueprint, render_template

web = Blueprint('frontend', __name__)

@web.route('/')
def index():
    return render_template('index.html')

@web.route('/admin')
def admin():
    return render_template('page.html', title="Admin", id='admin')


# This route is a catch-all route for anything
# beneath the /api-explorer endpoint. Allows
# the API explorer to function with client-side
# routing with react-router...
@web.route('/api-explorer')
# Should really replace this with trailing-slash removal
# middleware of some sort
@web.route('/api-explorer/')
@web.route('/api-explorer/<path:path>')
def api_explorer(path='/'):
    return render_template('page.html', title="API Explorer", id='api-explorer')

@web.route('/dz-samples')
def dz_samples():
    return render_template('page.html', title="Detrital Zircon samples", id='dz-samples')
