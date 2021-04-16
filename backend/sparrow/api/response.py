from starlette.responses import JSONResponse
from json import dumps
from typing import Any

from ..logs import get_logger
from ..encoders import JSONEncoder
from .exceptions import SerializationError
from .utils import format_transaction_time

log = get_logger(__name__)


class APIResponse(JSONResponse):
    # copied from https://github.com/perdy/flama/blob/master/flama/responses.py
    media_type = "application/json"

    def __init__(self, *args, **kwargs):
        self.schema = kwargs.pop("schema", None)
        self.total_count = kwargs.pop("total_count", None)
        self.status = kwargs.pop("status", "Success")
        self.transaction_time = kwargs.pop("transaction_time", None)
        self.to_dict = kwargs.pop("to_dict", False)
        super().__init__(*args, **kwargs)

    def render(self, content: Any):
        """Creates output JSON representation of the API route, optionally applying
        paging if it exists"""
        # Use output schema to validate and format data

        paging = getattr(content, "paging", None)
        page = {}
        if self.total_count is not None:
            page["total_count"] = self.total_count
        if paging is not None:
            page["next_page"] = paging.bookmark_next if paging.has_next else None
            page["previous_page"] = (
                paging.bookmark_previous if paging.has_previous else None
            )
        header = {"status": self.status}
        if self.transaction_time is not None:
            header['transaction_time'] = format_transaction_time(self.transaction_time)

        try:
            if self.schema is not None:
                content = self.schema.dump(content)
            if self.to_dict:
                # This helps us deal with sequence rows
                content = [c._asdict() for c in content]
        except Exception:
            raise SerializationError(status_code=500)

        return self._encode(dict(**header,data=content, **page))

    def _encode(self, content: Any) -> bytes:
        """Shim for starlette's JSONResponse (subclassed by Flama)
        that properly encodes Decimal and geometries.
        """
        return dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=JSONEncoder,
        ).encode("utf-8")
