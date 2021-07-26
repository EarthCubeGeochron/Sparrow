from sparrow.api.filters import BaseFilter, create_params
from sparrow.context import app_context
from webargs.fields import Str
from sqlalchemy import text, Table, or_


def get_document_tables(db):
    """returns array of document tables
    [project, sample, session]
    """
    document_names = ["project", "sample", "session"]

    doc_tables = []
    for name in document_names:
        doc_table = Table(
            f"{name}_document", db.meta, autoload_with=db.engine, schema="documents"
        )
        doc_tables.append(doc_table)
    return doc_tables


def session_joins(db, query):
    """make session joins to query

    join session_doc
    join project_doc
    join sample_doc
    """
    project_doc, sample_doc, session_doc = get_document_tables(db)

    session = db.model.session

    query = query.outerjoin(session_doc, session.id == session_doc.c.session_id)
    query = query.outerjoin(project_doc, session.project_id == project_doc.c.project_id)
    query = query.outerjoin(sample_doc, session.sample_id == sample_doc.c.sample_id)

    return query


def sample_joins(db, query):
    """make sample_doc joins to query"""
    project_doc, sample_doc, session_doc = get_document_tables(db)

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


def project_joins(db, query):
    project_doc, sample_doc, session_doc = get_document_tables(db)

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


def construct_query(db, model, search):
    """creates a query to the documents table"""
    project_doc, sample_doc, session_doc = get_document_tables(db)

    query = db.session.query(model)

    if model == getattr(db.model, "session"):
        query = session_joins(db, query)
    elif model == getattr(db.model, "sample"):
        query = sample_joins(db, query)
    else:
        query = project_joins(db, query)

    # construct filter using the match operator
    query = query.filter(
        or_(
            sample_doc.c.sample_token.match(search),
            project_doc.c.project_token.match(search),
            session_doc.c.session_token.match(search),
        )
    )

    return query


class OpenSearchFilter(BaseFilter):
    """
    Filter that leverages the document tokens for postgres full text search
    """

    key = "search"
    possible_models = ["project", "sample", "session"]

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

        return construct_query(db, self.model, search_query)
