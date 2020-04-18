from sparrow.plugins import SparrowPlugin
from sparrow.database.util import run_sql
from boto3 import client
from click import secho, command, option
from os import environ


class CloudDataPlugin(SparrowPlugin):
    """A base plugin for cloud data. Should be subclassed by importers."""
    name = "cloud-data"

    def __init__(self, app):
        super().__init__(app)
        self.auth = dict(
            endpoint=environ.get("SPARROW_S3_ENDPOINT", None),
            bucket=environ.get("SPARROW_S3_BUCKET", None),
            access_key=environ.get("SPARROW_S3_KEY", None),
            secret_key=environ.get("SPARROW_S3_SECRET", None))

        self.__fully_defined = all([i is not None for i in self.auth.values()])

        s3 = self.auth
        self.session = client('s3',
                              endpoint_url=s3['endpoint'],
                              aws_access_key_id=s3['access_key'],
                              aws_secret_access_key=s3['secret_key'])

    def iterate_objects(self):
        if not self.__fully_defined:
            secho("Not all required environment variables are provided.")
            return

        nkeys = 0
        paginator = self.session.get_paginator('list_objects')
        pages = paginator.paginate(Bucket=self.auth['bucket'])
        for page in pages:
            for obj in page['Contents']:
                yield obj
                nkeys += 1

    def get_object(self, key):
        res = self.session.get_object(Bucket=self.auth['bucket'], Key=key)
        return res['Body']

    def on_core_tables_initialized(self, db):
        # We need a separate column to store S3 ETags, which are almost like our
        # MD5 hashes, but not quite...
        run_sql(db.session, "ALTER TABLE data_file ADD COLUMN file_etag text UNIQUE")

    def process_objects(self, only_untracked=True):
        for obj in self.iterate_objects():
            already_exists = self.check_object(obj)
            if already_exists and only_untracked:
                continue
            body = self.get_object(obj['Key'])
            yield self.import_object(obj, body)

    def on_setup_cli(self, cli):
        # It might make sense to run cloud import operations
        # in a separate Docker container, but we do it in the
        # main container for now
        @command(name='import-cloud-data')
        @option("--redo", is_flag=True, default=False)
        def cmd(redo=False):
            """Import cloud data"""
            list(self.process_objects(only_untracked=not redo))
        cli.add_command(cmd)

    def check_object(self, obj):
        db = self.app.database
        # ETag is (almost) always the MD5. It could have a postfix
        # Hash values are stored as uuids and must be 32 chars long
        # https://docs.aws.amazon.com/AmazonS3/latest/API/RESTCommonResponseHeaders.html
        id = obj["ETag"].replace('"', '')
        model = db.session.query(db.model.data_file).filter_by(file_etag=id).first()
        return model is not None

    def import_object(self, meta, contents):
        raise Exception("Need to subclass and override this function")
