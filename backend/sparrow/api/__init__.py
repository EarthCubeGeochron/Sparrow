from flama import Flama

APIv2 = Flama(
    title="Sparrow API",
    version="2.0",
    description="An API for accessing geochemical data",
)


@APIv2.route("/", methods=["GET"])
def hello_world():
    """
    description:
        A test API base route.
    responses:
        200:
            description: It's alive!
    """
    return {"Hello": "world!"}
