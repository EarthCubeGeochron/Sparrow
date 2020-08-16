from flama import Flama
from sparrow.logs import get_logger
from ..database.mapper.util import classname_for_table

log = get_logger(__name__)


def hello_world():
    """
    description:
        A test API base route.
    responses:
        200:
            description: It's alive!
    """
    return {"Hello": "world!"}


class APIv2(Flama):
    def __init__(self, app):
        self._app = app
        super().__init__(
            title="Sparrow API",
            version="2.0",
            description="An API for accessing geochemical data",
        )
        self._add_routes()

    def _add_routes(self):
        self.add_route("/", hello_world, methods=["GET"])

        db = self._app.database

        for iface in db.interface:
            schema = iface()
            name = classname_for_table(schema.opts.model.__table__)
            log.info(name)

            def list_items() -> iface(many=True):
                schema = db.model_schema("sample")
                res = db.session.query(schema.opts.model).limit(100).all()
                return [schema.dump(r) for r in res]

            self.add_route("/" + name, list_items, methods=["GET"])
