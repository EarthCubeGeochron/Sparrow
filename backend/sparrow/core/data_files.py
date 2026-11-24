"""Sending a tracked data file to whoever asked for it."""

from os import environ
from typing import Optional

from sparrow.core.storage import get_object_store


def download_location(datafile) -> Optional[dict]:
    """How a data file can be fetched: an address to redirect to, its contents
    to pass on, or a path for the gateway to serve from the lab's data
    directory. None if it cannot be."""
    store = get_object_store()
    if store is not None:
        key = None
        if datafile.source_url is not None:
            key = store.key_for(datafile.source_url)
        if key is None and store.exists(datafile.file_path):
            key = datafile.file_path
        if key is not None and store.public:
            return {"url": store.download_url(key, filename=datafile.basename)}
        if key is not None:
            return {"stream": store.stream(key)}
    if "SPARROW_DATA_DIR" in environ:
        # X-Accel-Redirect: nginx serves the file, from where the directory is mounted
        return {"accel_redirect": f"/data/{datafile.file_path}"}
    return None
