from flask import (
    Blueprint,
    make_response,
    Response,
    render_template,
    current_app,
    abort,
)
from os.path import join
from .plugins import SparrowCorePlugin

web = Blueprint("frontend", __name__)


@web.route("/data-file/<string:uuid>")
def stream_data(uuid):
    # Send the user to the "protected" data dir to get the file with NGINX
    db = current_app.database
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
    v = current_app.config.get("LAB_NAME")
    if v != "Arizona LaserChron Center":
        abort(404)
    db = current_app.database
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


@web.route("/")
# This route is a catch-all route for anything
# beneath the / endpoint. Allows
# the API explorer to function with client-side
# routing with react-router...
@web.route("/<path:path>")
def index(path="/"):
    v = current_app.config.get("LAB_NAME")
    base_url = current_app.config.get("BASE_URL")
    # Hack to make browserSync work
    if base_url == "/":
        base_url = ""

    return render_template(
        "page.html",
        title=v,
        id="index",
        base_url=base_url,
        asset_dir=join(base_url, "assets"),
    )


class WebPlugin(SparrowCorePlugin):
    name = "web"

    def on_finalize_routes(self):
        self.app.register_blueprint(web, url_prefix="/")
