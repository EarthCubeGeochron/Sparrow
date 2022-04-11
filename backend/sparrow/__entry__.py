"""
Entrypoint for the application server. Should be served with an ASGI
server such as Hypercorn or Uvicorn.
"""

from .logs import setup_stderr_logs

setup_stderr_logs()

from .context import get_sparrow_app

app = get_sparrow_app()
app.bootstrap(init=True, use_schema_cache=False)
