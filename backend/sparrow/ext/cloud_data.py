from boto3 import client
from click import secho, command, option
from os import environ
from sparrow.plugins import SparrowPlugin
from sparrow.database.util import run_sql


class CloudDataPlugin(SparrowPlugin):
    """A base plugin for cloud data. Should be subclassed by importers."""

    name = "cloud-data"

    def __init__(self, app):
        super().__init__(app)
        self.auth = dict(
            endpoint=environ.get("SPARROW_S3_ENDPOINT", None),
            bucket=environ.get("SPARROW_S3_BUCKET", None),
            access_key=environ.get("SPARROW_S3_KEY", None),
            secret_key=environ.get("SPARROW_S3_SECRET", None),
        )

        self.__fully_defined = all([i is not None for i in self.auth.values()])

        s3 = self.auth
        self.session = client(
            "s3",
            endpoint_url=s3["endpoint"],
            aws_access_key_id=s3["access_key"],
            aws_secret_access_key=s3["secret_key"],
        )

    def iterate_objects(self, only_untracked=False):
        if not self.__fully_defined:
            secho("Not all required environment variables are provided.")
            return

        nkeys = 0
        paginator = self.session.get_paginator("list_objects")
        pages = paginator.paginate(Bucket=self.auth["bucket"])
        for page in pages:
            for obj in page["Contents"]:
                if only_untracked and self._already_tracked(obj):
                    continue
                yield obj
                nkeys += 1

    def get_body(self, key):
        res = self.session.get_object(Bucket=self.auth["bucket"], Key=key)
        return res["Body"]

    def on_core_tables_initialized(self, db):
        # We need a separate column to store S3 ETags, which are almost like our
        # MD5 hashes, but not quite...
        run_sql(db.session, "ALTER TABLE data_file ADD COLUMN file_etag text UNIQUE")

    def _instance_for_meta(self, meta):
        db = self.app.database
        # ETag is (almost) always the MD5. It could have a postfix
        # Hash values are stored as uuids and must be 32 chars long
        # https://docs.aws.amazon.com/AmazonS3/latest/API/RESTCommonResponseHeaders.html
        id = meta["ETag"].replace('"', "")
        return db.session.query(db.model.data_file).filter_by(file_etag=id).first()

    def _already_tracked(self, meta):
        return self._instance_for_meta(meta) is not None

    def get_download_url(self, key):
        # If we have an access-controlled bucket, we need to get a "presigned" URL
        # https://www.digitalocean.com/community/questions/signed-urls-for-private-objects-in-spaces
        return self.session.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.auth["bucket"], "Key": key},
            ExpiresIn=300,
        )
