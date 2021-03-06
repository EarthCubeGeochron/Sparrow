from .base import construct_app
from webargs_starlette import WebargsHTTPException
from starlette.responses import JSONResponse

# For some reason, adding logging in this file seems to kill logging in the entire
# application

app = construct_app()


# @app.exception_handler(WebargsHTTPException)
# async def http_exception(request, exc):
#     return JSONResponse(exc.messages, status_code=exc.status_code, headers=exc.headers)
