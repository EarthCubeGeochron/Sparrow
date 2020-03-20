from sparrow.plugins import SparrowPlugin
from boto3 import client
from click import secho, command, option
from os import environ

class CloudDataPlugin(SparrowPlugin):
    """A base plugin for cloud data. Should be subclassed by importers."""
    name = "cloud-data"

    def on_setup_cli(self, cli):
        # It might make sense to run cloud import operations
        # in a separate Docker container, but we do it in the
        # main container for now
        @command(name='import-cloud-data')
        @option("--overwrite", is_flag=True, default=False)
        def cmd(*args, **kwargs):
            """Import cloud data"""

            s3 = dict(
                endpoint=environ.get("SPARROW_S3_ENDPOINT", None),
                bucket=environ.get("SPARROW_S3_BUCKET", None),
                access_key=environ.get("SPARROW_S3_KEY", None),
                secret_key=environ.get("SPARROW_S3_SECRET", None))

            fully_defined = all([i is not None for i in s3.values()])
            if not fully_defined:
                secho("Not all required environment variables are provided.")
                return

            session = client('s3',
                             endpoint_url=s3['endpoint'],
                             aws_access_key_id=s3['access_key'],
                             aws_secret_access_key=s3['secret_key'])

            nkeys = 0
            paginator = session.get_paginator('list_objects')
            pages = paginator.paginate(Bucket=s3['bucket'])
            for page in pages:
                for obj in page['Contents']:
                    self.check_object(obj)
                    nkeys += 1
                    print(obj['Key'])
            print(nkeys)

        cli.add_command(cmd)

    def check_object(self, obj):
        pass
