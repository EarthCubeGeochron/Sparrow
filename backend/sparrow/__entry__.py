"""
Entrypoint for the application server. Should be served with an ASGI
server such as Hypercorn or Uvicorn.
"""

from .context import get_sparrow_app
from .logs import setup_stderr_logs

setup_stderr_logs()
app = get_sparrow_app()
app.bootstrap()
