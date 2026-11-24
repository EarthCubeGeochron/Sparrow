"""Sinks that need no database: a dry run, and a lab's import API."""

from dataclasses import dataclass, field
from typing import Optional

from .models import TopLevelRecord
from .pipeline import SourceFile


@dataclass
class DryRunSink:
    """Collects records without sending them anywhere. Reading a file already
    validates it, so a dry run reports every file a real run would reject."""

    records: list[TopLevelRecord] = field(default_factory=list)
    failures: dict[str, str] = field(default_factory=dict)

    def begin(self, source: SourceFile, *, redo: bool = False) -> bool:
        return True

    def load(self, source: SourceFile, records: list[TopLevelRecord]) -> None:
        self.records.extend(records)

    def fail(self, source: SourceFile, error: Exception) -> None:
        self.failures[str(source.path)] = str(error)


class APIError(Exception):
    pass


@dataclass
class APISink:
    """Sends records to a running Sparrow lab over its import API.

    The lab decides what a record matches; this sink keeps no state, so files
    are not tracked and every run sends every file."""

    base_url: str
    token: Optional[str] = None
    timeout: float = 60

    def _client(self):
        import httpx

        headers = {}
        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"
        return httpx.Client(
            base_url=self.base_url.rstrip("/"), headers=headers, timeout=self.timeout
        )

    def begin(self, source: SourceFile, *, redo: bool = False) -> bool:
        return True

    def load(self, source: SourceFile, records: list[TopLevelRecord]) -> None:
        with self._client() as client:
            for record in records:
                res = client.put(
                    f"/api/v2/import-data/models/{record.model_name}",
                    json={"data": record.to_import_data()},
                )
                if res.status_code >= 400:
                    raise APIError(f"{res.status_code}: {res.text}")

    def fail(self, source: SourceFile, error: Exception) -> None:
        pass
