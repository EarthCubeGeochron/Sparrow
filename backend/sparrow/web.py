from flask import Blueprint, Response, current_app, abort, Flask
from asgiref.wsgi import WsgiToAsgi
from .plugins import SparrowCorePlugin
from .context import get_sparrow_app
from .settings import LAB_NAME

web = Blueprint("frontend", __name__)


@web.route("/data-file/<string:uuid>")
def stream_data(uuid):
    # Send the user to the "protected" data dir to get the file with NGINX
    db = get_sparrow_app().database
    m = db.model.data_file

    datafile = db.session.query(m).get(uuid)
    if datafile is None:
        abort(404)

    basename = datafile.basename
    res = Response()
    res.headers["Content-Type"] = ""
    res.headers["Content-Disposition"] = 'attachment; filename="' + basename + '"'
    res.headers["X-Accel-Redirect"] = "/data/" + datafile.file_path
    return res


# This route is only for LaserChron but we don't have a good
# plugin interface for the backend yet so it'll just be dead code
# for other users
@web.route("/data-table/<string:uuid>.csv")
def get_csv(uuid):
    if LAB_NAME != "Arizona LaserChron Center":
        abort(404)
    db = get_sparrow_app().database
    m = db.model.data_file

    datafile = db.session.query(m).get(uuid)
    if datafile is None:
        abort(404)

    csv = datafile.csv_data.decode()
    basename = datafile.basename

    res = Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; 'filename={basename}.csv'"},
    )
    return res


class WebPlugin(SparrowCorePlugin):
    name = "web"
    sparrow_version = ">=2.*"

    def on_finalize_routes(self):
        app = Flask(__name__)
        app.register_blueprint(web, url_prefix="/")
        self.app.mount("/", WsgiToAsgi(app))
