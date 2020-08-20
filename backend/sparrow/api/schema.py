from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from starlette_apispec import APISpecSchemaGenerator

schemas = APISpecSchemaGenerator(
    APISpec(
        title="Sparrow",
        version="2.0",
        openapi_version="3.0.0",
        info={"Sparrow": "Serving up geochemistry data"},
        plugins=[MarshmallowPlugin()],
    )
)

def schema(request):
    return schemas.OpenAPIResponse(request=request)
