"""
A pipeline turns files into records. It does not know where they go.

Running one needs only this package, so a pipeline can be developed and
rehearsed on a laptop; the same object is what a Sparrow server runs as a task.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import md5
from pathlib import Path
from typing import Iterable, Optional, Protocol

from .models import TopLevelRecord


@dataclass(frozen=True)
class SourceFile:
    """A file a pipeline reads, identified by its contents."""

    path: Path
    file_hash: str
    mtime: datetime
    # Kind of file, as recorded by Sparrow (e.g. "PyChron Interpreted Age")
    file_type: Optional[str] = None
    # Where the file can be retrieved from, if not from its path
    source_url: Optional[str] = None

    @classmethod
    def from_path(cls, path: Path, **kwargs) -> "SourceFile":
        path = Path(path)
        digest = md5()
        with path.open("rb") as f:
            for block in iter(lambda: f.read(1 << 20), b""):
                digest.update(block)
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        return cls(path=path, file_hash=digest.hexdigest(), mtime=mtime, **kwargs)


class Pipeline:
    """Subclass, set `name`, and implement `read`."""

    name: str
    file_type: Optional[str] = None
    # Files to read when a pipeline is pointed at a directory
    pattern: str = "*"

    def discover(self, root: Path) -> Iterable[Path]:
        root = Path(root)
        if root.is_file():
            yield root
            return
        yield from sorted(p for p in root.rglob(self.pattern) if p.is_file())

    def source_url(self, path: Path) -> Optional[str]:
        return None

    def read(self, path: Path) -> Iterable[TopLevelRecord]:
        """Yield the records a file holds. Raise to reject the file."""
        raise NotImplementedError


class Sink(Protocol):
    """Where records go: nowhere (a dry run), a lab's API, or its database."""

    def begin(self, source: SourceFile, *, redo: bool = False) -> bool:
        """Whether this file should be read; false if it is already loaded."""

    def load(self, source: SourceFile, records: list[TopLevelRecord]) -> None:
        """Load a file's records together."""

    def fail(self, source: SourceFile, error: Exception) -> None:
        """Note that a file could not be read or loaded."""


@dataclass
class FileResult:
    source: SourceFile
    status: str  # "loaded", "skipped" or "failed"
    n_records: int = 0
    error: Optional[str] = None


@dataclass
class RunReport:
    files: list[FileResult] = field(default_factory=list)

    def count(self, status: str) -> int:
        return sum(1 for f in self.files if f.status == status)

    @property
    def ok(self) -> bool:
        return self.count("failed") == 0


def run_pipeline(
    pipeline: Pipeline,
    paths: Iterable[Path],
    sink: Sink,
    *,
    redo: bool = False,
    stop_on_error: bool = False,
) -> RunReport:
    """Read each file and hand its records to a sink, one file at a time."""
    report = RunReport()
    for root in paths:
        for path in pipeline.discover(Path(root)):
            source = SourceFile.from_path(
                path, file_type=pipeline.file_type, source_url=pipeline.source_url(path)
            )
            if not sink.begin(source, redo=redo):
                report.files.append(FileResult(source, "skipped"))
                continue
            try:
                records = list(pipeline.read(path))
                sink.load(source, records)
            except Exception as error:
                if stop_on_error:
                    raise
                sink.fail(source, error)
                report.files.append(FileResult(source, "failed", error=str(error)))
                continue
            report.files.append(FileResult(source, "loaded", len(records)))
    return report
