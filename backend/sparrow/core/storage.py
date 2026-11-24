"""
Object storage for a lab's files. The backend reaches files only through a
bucket, so it needs no directory on the machine it runs on; a lab that keeps
files on a disk or a shared drive puts `rclone serve s3` in front of them.
"""

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from fnmatch import fnmatch
from os import environ
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from typing import Iterator, Optional
from urllib.parse import urlparse

from sparrow.logs import get_logger

log = get_logger(__name__)


@dataclass(frozen=True)
class StoredObject:
    key: str
    etag: str
    size: int
    mtime: datetime

    @property
    def md5(self) -> Optional[str]:
        """The MD5 of the contents, where the store reports one. An ETag with a
        suffix belongs to a multipart upload, and is not a hash of the file."""
        etag = self.etag.strip('"')
        if len(etag) == 32 and "-" not in etag:
            return etag
        return None


@dataclass
class ObjectStore:
    bucket: str
    endpoint: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    # Keys are kept beneath this, so labs can share a bucket
    prefix: str = ""
    # Whether a browser can reach the endpoint. If not (a gateway inside the
    # lab's own network), the backend passes downloads through itself.
    public: bool = True

    def __post_init__(self):
        self.prefix = self.prefix.strip("/")
        self._client = None

    @classmethod
    def from_environment(cls) -> Optional["ObjectStore"]:
        bucket = environ.get("SPARROW_S3_BUCKET")
        if not bucket:
            return None
        return cls(
            bucket=bucket,
            endpoint=environ.get("SPARROW_S3_ENDPOINT") or None,
            access_key=environ.get("SPARROW_S3_KEY") or None,
            secret_key=environ.get("SPARROW_S3_SECRET") or None,
            prefix=environ.get("SPARROW_S3_PREFIX", ""),
            public=environ.get("SPARROW_S3_PRIVATE", "0") not in ("1", "true"),
        )

    @property
    def client(self):
        if self._client is None:
            from boto3 import client

            self._client = client(
                "s3",
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
        return self._client

    # -- naming -------------------------------------------------------------

    def _full_key(self, key: str) -> str:
        key = key.lstrip("/")
        return f"{self.prefix}/{key}" if self.prefix else key

    def uri(self, key: str) -> str:
        return f"s3://{self.bucket}/{self._full_key(key)}"

    def key_for(self, uri: str) -> Optional[str]:
        """The key of an `s3://` address in this store, or None if it is elsewhere."""
        parsed = urlparse(uri)
        if parsed.scheme != "s3" or parsed.netloc != self.bucket:
            return None
        key = parsed.path.lstrip("/")
        if self.prefix:
            if not key.startswith(self.prefix + "/"):
                return None
            key = key[len(self.prefix) + 1 :]
        return key

    # -- objects ------------------------------------------------------------

    def list(self, prefix: str = "", pattern: str = "*") -> Iterator[StoredObject]:
        """Objects beneath a prefix whose file name matches a pattern."""
        full_prefix = self._full_key(prefix)
        strip = len(self.prefix) + 1 if self.prefix else 0
        paginator = self.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=full_prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"][strip:]
                if key.endswith("/") or not fnmatch(PurePosixPath(key).name, pattern):
                    continue
                yield StoredObject(
                    key=key,
                    etag=obj["ETag"],
                    size=obj["Size"],
                    mtime=obj["LastModified"],
                )

    def exists(self, key: str) -> bool:
        from botocore.exceptions import ClientError

        try:
            self.client.head_object(Bucket=self.bucket, Key=self._full_key(key))
        except ClientError:
            return False
        return True

    def upload(self, path: Path, key: str) -> str:
        self.client.upload_file(str(path), self.bucket, self._full_key(key))
        return self.uri(key)

    @contextmanager
    def downloaded(self, key: str) -> Iterator[Path]:
        """A local copy of an object, kept for as long as it is in use."""
        with TemporaryDirectory(prefix="sparrow-") as tmp:
            # Keep the key's shape: pipelines read names and parent directories
            path = Path(tmp) / key
            path.parent.mkdir(parents=True, exist_ok=True)
            self.client.download_file(self.bucket, self._full_key(key), str(path))
            yield path

    def stream(self, key: str):
        """The object's contents, in chunks."""
        res = self.client.get_object(Bucket=self.bucket, Key=self._full_key(key))
        return res["Body"].iter_chunks(1 << 16)

    def download_url(
        self, key: str, *, filename: Optional[str] = None, expires: int = 300
    ) -> str:
        """A short-lived address a browser can fetch the object from."""
        params = {"Bucket": self.bucket, "Key": self._full_key(key)}
        if filename is not None:
            params["ResponseContentDisposition"] = f'attachment; filename="{filename}"'
        return self.client.generate_presigned_url(
            ClientMethod="get_object", Params=params, ExpiresIn=expires
        )


_store: Optional[ObjectStore] = None


def get_object_store() -> Optional[ObjectStore]:
    """The lab's object store, or None if it keeps files in a directory."""
    global _store
    if _store is None:
        _store = ObjectStore.from_environment()
    return _store


def set_object_store(store: Optional[ObjectStore]):
    global _store
    _store = store
