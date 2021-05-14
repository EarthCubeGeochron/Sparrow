Sparrow's database backup service enables on-demand and periodic backups of
Sparrow's database to both local directories, specified by `SPARROW_BACKUP_DIR`,
and remote S3 buckets, specified by `SPARROW_BACKUP_BUCKET` and other S3
connection variables.  The `SPARROW_LAB_ID` variable must also be set to prefix
the backups.
