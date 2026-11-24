"""
A pipeline turns files into records. It does not know where they go.

Running one needs only this package, so a pipeline can be developed and
rehearsed on a laptop; the same object is what a Sparrow server runs as a task.
"""

from contextlib import AbstractContextManager, nullcontext
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import md5
from pathlib import Path
from typing import Callable, Iterable, Optional, Protocol

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


@dataclass
class Source:
    """A file to read, and how to get hold of it on this machine. For a local
    file that is its path; for an object in a bucket it is a download."""

    file: SourceFile
    open: Callable[[], AbstractContextManager[Path]]

    @classmethod
    def local(cls, file: SourceFile) -> "Source":
        return cls(file, lambda: nullcontext(file.path))


def run_sources(
    pipeline: Pipeline,
    sources: Iterable[Source],
    sink: Sink,
    *,
    redo: bool = False,
    stop_on_error: bool = False,
) -> RunReport:
    """Read each source and hand its records to a sink, one file at a time."""
    report = RunReport()
    for source in sources:
        file = source.file
        if not sink.begin(file, redo=redo):
            report.files.append(FileResult(file, "skipped"))
            continue
        try:
            with source.open() as path:
                records = list(pipeline.read(path))
            sink.load(file, records)
        except Exception as error:
            if stop_on_error:
                raise
            sink.fail(file, error)
            report.files.append(FileResult(file, "failed", error=str(error)))
            continue
        report.files.append(FileResult(file, "loaded", len(records)))
    return report


def local_sources(pipeline: Pipeline, paths: Iterable[Path]) -> Iterable[Source]:
    for root in paths:
        for path in pipeline.discover(Path(root)):
            yield Source.local(
                SourceFile.from_path(
                    path,
                    file_type=pipeline.file_type,
                    source_url=pipeline.source_url(path),
                )
            )


def run_pipeline(
    pipeline: Pipeline,
    paths: Iterable[Path],
    sink: Sink,
    *,
    redo: bool = False,
    stop_on_error: bool = False,
) -> RunReport:
    """Read local files and hand their records to a sink."""
    return run_sources(
        pipeline,
        local_sources(pipeline, paths),
        sink,
        redo=redo,
        stop_on_error=stop_on_error,
    )
