import json

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import DeclarativeMeta

from .util import run_sql_file, working_directory

metadata = MetaData()

class Database:
    def __init__(self, cfg):
        self.engine = create_engine(cfg)
        metadata.create_all(bind=self.engine)
        self.meta = metadata
        self.session = sessionmaker(bind=self.engine)()

    def exec_sql(self, *args):
        run_sql_file(self.engine, *args)

    def initialize(self, drop=False):
        with working_directory(__file__):
            if drop:
                self.exec_sql("sql/00-drop-tables.sql")
            self.exec_sql("sql/01-setup-database.sql")
            self.exec_sql("sql/02-create-tables.sql")
            self.exec_sql("sql/03-create-views.sql")
            self.exec_sql("sql/04-populate-vocabulary.sql")
