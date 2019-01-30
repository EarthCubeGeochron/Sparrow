from click import secho

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.schema import Table
from sqlalchemy.sql import ClauseElement

from .app import App
from .util import run_sql_file, working_directory

metadata = MetaData()

# For automapping
def name_for_scalar_relationship(base, local_cls, referred_cls, constraint):
    return "_"+referred_cls.__name__.lower()

def get_or_create(session, model, defaults=None, **kwargs):
    """
    Get an instance of a model, or create it if it doesn't
    exist.
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.items()
            if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        return instance, True

class Database:
    def __init__(self, cfg=None):
        """
        We can pass a connection string, a FLASK application
        with the appropriate configuration, or nothing, in which
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
        self.automap_base = None

    def exec_sql(self, *args):
        run_sql_file(self.engine, *args)

    def reflect_table(self, tablename, schema='public', **kwargs):
        meta = MetaData(schema=schema)
        return Table(tablename, meta,
            autoload=True, autoload_with=self.engine, **kwargs)

    @property
    def mapped_classes(self):
        """
        Map all tables in the database to SQLAlchemy models

        https://docs.sqlalchemy.org/en/latest/orm/extensions/automap.html
        """
        if self.automap_base is not None:
            return self.automap_base.classes
        Base = automap_base()
        Base.prepare(self.engine, reflect=True,
            name_for_scalar_relationship=name_for_scalar_relationship)
        self.automap_base = Base
        return self.automap_base.classes

    def initialize(self, drop=False):
        secho("Creating core schema...", bold=True)
        with working_directory(__file__):
            if drop:
                self.exec_sql("sql/00-drop-tables.sql")
            self.exec_sql("sql/01-setup-database.sql")
            self.exec_sql("sql/02-create-tables.sql")
            self.exec_sql("sql/03-create-views.sql")
            self.exec_sql("sql/04-populate-vocabulary.sql")

        init_sql = self.config.get("INIT_SQL", None)
        if init_sql is not None:
            secho("\nCreating schema extensions...", bold=True)
            for s in init_sql:
                self.exec_sql(s)
