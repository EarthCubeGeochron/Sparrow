from flask import Blueprint, render_template

web = Blueprint('frontend', __name__)

@web.route('/')
def index():
    return render_template('index.html')

@web.route('/api-explorer/<path>')
@web.route('/api-explorer')
def api_explorer(path='/'):
    return render_template('page.html', title="API Explorer", id='api-explorer')
