"""
Entrypoint for the application server. Should be served with an ASGI
server such as Hypercorn or Uvicorn.
"""

from ..logs import setup_stderr_logs
from .base import Sparrow

setup_stderr_logs()
app = Sparrow(debug=True)
