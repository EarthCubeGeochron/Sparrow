from contextlib import contextmanager
from pathlib import Path
from click import secho
from os import environ

from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.schema import ForeignKey, Column
from sqlalchemy.types import Integer
from sqlalchemy.exc import IntegrityError

from .util import run_sql_file, run_query, get_or_create
from .models import User, Project, Session, DatumType
from .mapper import MappedDatabaseMixin
from ..logs import get_logger
from ..util import relative_path

metadata = MetaData()

log = get_logger(__name__)


class Database(MappedDatabaseMixin):
    def __init__(self, app=None):
        """
        We can pass a connection string, a **Flask** application object
        with the appropriate configuration, or nothing, in which
        case we will try to infer the correct database from
        the SPARROW_BACKEND_CONFIG file, if available.
        """
        self.config = None
        if app is None:
            from ..app import App
            # Set config from environment variable
            app = App(__name__)
            # Load plugins
        self.app = app

        self.config = app.config
        db_conn = self.config.get("DATABASE")
        # Override with environment variable
        envvar = environ.get("SPARROW_DATABASE", None)
        if envvar is not None:
            db_conn = envvar
        self.engine = create_engine(db_conn)
        metadata.create_all(bind=self.engine)
        self.meta = metadata

        # Scoped session for database
        # https://docs.sqlalchemy.org/en/13/orm/contextual.html#unitofwork-contextual
        # https://docs.sqlalchemy.org/en/13/orm/session_basics.html#session-faq-whentocreate
        self._session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(self._session_factory)
        # Use the self.session_scope function to more explicitly manage sessions.

        self.lazy_automap()

    def automap(self):
        super().automap()
        # Database models we have extended with our own functions
        # (we need to add these to the automapped classes since they are not
        #  included by default)
        # TODO: there is probably a way to do this without having to manually register the models
        self.register_models(User, Project, Session, DatumType)
        # Register a new class
        # Automap the core_view.datum relationship
        cls = self.automap_view("datum",
            Column("datum_id", Integer, primary_key=True),
            Column("analysis_id", Integer, ForeignKey(self.table.analysis.c.id)),
            Column("session_id", Integer, ForeignKey(self.table.session.c.id)),
            schema='core_view')
        self.register_models(cls)

    @contextmanager
    def session_scope():
        """Provide a transactional scope around a series of operations."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def load_data(self, model_name, data):
        iface = getattr(self.interface, model_name)
        self.session.rollback()
        try:
            with self.session.no_autoflush:
                res = iface().load(data, session=self.session, transient=True)
                self.session.flush()
                self.session.merge(res)
                #sess = self.session()
                #sess.transaction._rollback_exception = None
                #    import pdb; pdb.set_trace()
            # insp = inspect(res)
            # import pdb; pdb.set_trace()
            # print(insp)
            #self.session.merge(res)
            self.session.commit()
            return res
        except Exception as err:
            self.session.rollback()
            raise err

    def get_instance(self, model_name, filter_params):
        iface = getattr(self.interface, model_name)
        res = iface().load(filter_params, session=self.session, partial=True)
        return res

    def exec_sql(self, fn):
        secho(Path(fn).name, fg='cyan', bold=True)
        run_sql_file(self.session, str(fn))

    def exec_query(self, *args):
        run_query(self.session, *args)

    @property
    def inspector(self):
        if self.__inspector__ is None:
            self.__inspector__ = inspect(self.engine)
        return self.__inspector__

    def entity_names(self, **kwargs):
        """
        Returns an iterator of names of *schema objects*
        (both tables and views) from a the database.
        """
        yield from self.inspector.get_table_names(**kwargs)
        yield from self.inspector.get_view_names(**kwargs)

    def get(self, model, *args, **kwargs):
        if isinstance(model, str):
            model = getattr(self.model, model)
        return self.session.query(model).get(*args,**kwargs)

    def get_or_create(self, model, **kwargs):
        """
        Get an instance of a model, or create it if it doesn't
        exist.
        """
        if isinstance(model, str):
            model = getattr(self.model, model)
        return get_or_create(self.session, model, **kwargs)

    def initialize(self, drop=False):
        secho("Creating core schema...", bold=True)

        if drop:
            fp = relative_path(__file__, "procedures", "drop-all-tables.sql")
            self.exec_sql(fp)

        p = Path(relative_path(__file__, "fixtures"))
        filenames = list(p.glob("*.sql"))
        filenames.sort()

        for fn in filenames:
            self.exec_sql(fn)

        try:
            self.app.run_hook('core-tables-initialized', self)
        except AttributeError as err:
            secho("Could not load plugins", fg='red', dim=True)
