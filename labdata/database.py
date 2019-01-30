import json
from os import environ

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.schema import Table

from .app import App
from .util import run_sql_file, working_directory

metadata = MetaData()

class Database:
    def __init__(self, cfg=None):
        """
        We can pass a connection string, a FLASK application
        with the appropriate config set, or nothing, in which
        case we will try to infer the correct database from
        the LABDATA_CONFIG file, if available.
        """
        self.config = None
        if cfg is None:
            # Set config from environment variable
            cfg = App(__name__)
        if hasattr(cfg,'config'):
            cfg = cfg.config
        self.config = cfg
        db_conn = self.config.get("DATABASE")
        self.engine = create_engine(db_conn)
        metadata.create_all(bind=self.engine)
        self.meta = metadata
        self.session = sessionmaker(bind=self.engine)()

    def exec_sql(self, *args):
        run_sql_file(self.engine, *args)

    def reflect_table(self, tablename, schema='public', **kwargs):
        meta = MetaData(schema=schema)
        return Table(tablename, meta,
            autoload=True, autoload_with=self.engine, **kwargs)

    def initialize(self, drop=False):
        with working_directory(__file__):
            if drop:
                self.exec_sql("sql/00-drop-tables.sql")
            self.exec_sql("sql/01-setup-database.sql")
            self.exec_sql("sql/02-create-tables.sql")
            self.exec_sql("sql/03-create-views.sql")
            self.exec_sql("sql/04-populate-vocabulary.sql")

        init_sql = self.config.get("INIT_SQL", None)
        if init_sql is not None:
            for s in init_sql:
                self.exec_sql(s)
