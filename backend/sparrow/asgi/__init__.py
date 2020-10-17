from .base import construct_app
from webargs_starlette import WebargsHTTPException
from starlette.responses import JSONResponse
from sparrow.logs import get_logger

app = construct_app()

log = get_logger(__name__)


@app.exception_handler(WebargsHTTPException)
async def http_exception(request, exc):
    log.debug(exc.messages)
    return JSONResponse(exc.messages, status_code=exc.status_code, headers=exc.headers)
