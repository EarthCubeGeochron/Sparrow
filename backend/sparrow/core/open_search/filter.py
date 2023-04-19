from sparrow.core.api.filters import BaseFilter, create_params
from sparrow.core.context import app_context
from webargs.fields import Str
from sqlalchemy import text, Table, or_
from contextvars import ContextVar
from sparrow.logs import get_logger

doc_table_cache = ContextVar("doc_table_cache")

log = get_logger(__name__)


def get_document_tables(db):
    """returns array of document tables
    [project, sample, session]
    """
    if doc_table_cache.get(None) is not None:
        return doc_table_cache.get(None)

    document_names = ["project", "sample", "session"]

    doc_tables = []
    for name in document_names:
        doc_table = Table(
            f"{name}_document", db.metadata, autoload_with=db.engine, schema="documents"
        )
        doc_tables.append(doc_table)

    doc_table_cache.set(doc_tables)
    return doc_tables


def session_joins(db, query, document_tables):
    """make session joins to query

    join session_doc
    join project_doc
    join sample_doc
    """
    project_doc, sample_doc, session_doc = document_tables

    session = db.model.session

    query = query.outerjoin(session_doc, session.id == session_doc.c.session_id)
    query = query.outerjoin(project_doc, session.project_id == project_doc.c.project_id)
    query = query.outerjoin(sample_doc, session.sample_id == sample_doc.c.sample_id)

    return query


def sample_joins(db, query, document_tables):
    """make sample_doc joins to query"""
    project_doc, sample_doc, session_doc = document_tables

    sample = db.model.sample
    project = db.model.project
    session = db.model.session

    query = query.outerjoin(sample_doc, sample.id == sample_doc.c.sample_id)
    query = query.outerjoin(sample.project_collection).outerjoin(
        project_doc, project.id == project_doc.c.project_id
    )
    query = query.outerjoin(sample.session_collection).outerjoin(
        session_doc, session.id == session_doc.c.session_id
    )

    return query


def project_joins(db, query, document_tables):
    project_doc, sample_doc, session_doc = document_tables

    sample = db.model.sample
    project = db.model.project
    session = db.model.session

    query = query.outerjoin(project_doc, project.id == project_doc.c.project_id)
    query = query.outerjoin(project.sample_collection).outerjoin(
        sample_doc, sample.id == sample_doc.c.sample_id
    )
    query = query.outerjoin(session, session.project_id == project.id).outerjoin(
        session_doc, session.id == session_doc.c.session_id
    )

    return query


def construct_query(db, model, search, document_tables):
    """creates a query to the documents table"""
    project_doc, sample_doc, session_doc = document_tables

    query = db.session.query(model)

    if model == getattr(db.model, "session"):
        log.info("session document query")
        query = session_joins(db, query, document_tables)
    elif model == getattr(db.model, "sample"):
        log.info("sample document query")
        query = sample_joins(db, query, document_tables)
    else:
        log.info("project document query")
        query = project_joins(db, query, document_tables)

    tsquery = text("to_tsquery(:search)")
    # construct filter using the match operator
    query = query.filter(
        or_(
            sample_doc.c.sample_token.op("@@")(tsquery),
            project_doc.c.project_token.op("@@")(tsquery),
            session_doc.c.session_token.op("@@")(tsquery),
        )
    ).params(search=search + ":*")

    return query


class OpenSearchFilter(BaseFilter):
    """
    Filter that leverages the document tokens for postgres full text search
    """

    key = "search"
    possible_models = ["project", "sample", "session"]

    def __init__(self, model, schema):
        self.project_document = None
        self.sample_document = None
        self.session_document = None
        super().__init__(model, schema=schema)

    def check_document_tables(self, db):
        if self.project_document is None:
            project, sample, session = get_document_tables(db)
            self.project_document = project
            self.sample_document = sample
            self.session_document = session

    @property
    def params(self):
        d = "A query string to search by"
        e = ["?search=basalt"]
        des = create_params(d, e)
        return {self.key: Str(description=des)}

    def should_apply(self):
        db = app_context().database

        apply = False
        for model in self.possible_models:
            if self.model == getattr(db.model, model):
                apply = True
                break
        return apply

    def apply(self, args, query):
        if self.key not in args:
            return query
        search_query = args[self.key]

        search_query = " & ".join(search_query.split())  ## breaks sentences into words
        db = app_context().database

        self.check_document_tables(db)
        document_tables = [
            self.project_document,
            self.sample_document,
            self.session_document,
        ]

        return construct_query(db, self.model, search_query, document_tables)
