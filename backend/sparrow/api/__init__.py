from flama import Flama


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
        super().__init__(
            title="Sparrow API",
            version="2.0",
            description="An API for accessing geochemical data",
        )
        self._add_routes()

    def _add_routes(self):
        self.add_route("/", hello_world, methods=["GET"])
