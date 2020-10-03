"""
Entrypoint for the application server. Should be served with an ASGI
server such as Hypercorn or Uvicorn.
"""

from sparrow.logs import setup_stderr_logs
from sparrow.asgi import construct_app

setup_stderr_logs()
app = construct_app()
