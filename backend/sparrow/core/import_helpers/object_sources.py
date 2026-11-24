"""Files in the lab's object store, as sources for a pipeline."""

from contextlib import contextmanager
from hashlib import md5
from pathlib import Path
from typing import Iterable

from sparrow.core.storage import ObjectStore, StoredObject
from sparrow.pipelines import Pipeline, Source, SourceFile


def _hash_file(path: Path) -> str:
    digest = md5()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _source(pipeline: Pipeline, store: ObjectStore, obj: StoredObject) -> Source:
    held = []

    def fetch() -> Path:
        # Downloaded at most once, and only if the file is going to be read
        if not held:
            ctx = store.downloaded(obj.key)
            held.append((ctx, ctx.__enter__()))
        return held[0][1]

    @contextmanager
    def opened():
        try:
            yield fetch()
        finally:
            for ctx, _ in held:
                ctx.__exit__(None, None, None)
            held.clear()

    # The store's own hash decides whether a file is new without fetching it
    file_hash = obj.md5 or _hash_file(fetch())
    file = SourceFile(
        path=Path(obj.key),
        file_hash=file_hash,
        mtime=obj.mtime,
        file_type=pipeline.file_type,
        source_url=store.uri(obj.key),
    )
    return Source(file, opened)


def stored_sources(
    pipeline: Pipeline, store: ObjectStore, prefixes: Iterable[str] = ("",)
) -> Iterable[Source]:
    for prefix in prefixes:
        # A full address names the same thing as its key
        key = store.key_for(prefix) if prefix.startswith("s3://") else prefix
        if key is None:
            raise ValueError(f"{prefix} is not in the lab's object store")
        for obj in store.list(key, pattern=pipeline.pattern):
            yield _source(pipeline, store, obj)
