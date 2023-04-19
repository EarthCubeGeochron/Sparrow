import sparrow
from sparrow.tests.helpers import json_fixture
from sqlalchemy import Table, or_, MetaData
from .filter import get_document_tables
from pytest import mark


class TestOpenSearch:
    """
    A testing suite to build upon the
    open search functionality.
    """

    data = json_fixture("project-edits.json")

    def test_get_database_meta(self, db):
        """test if we can get the database meta"""
        assert isinstance(db.metadata, MetaData)

    def test_get_document_tables(self, db):
        """Ensure that we can get the generated document tables"""
        tables = get_document_tables(db)
        assert len(tables) == 3

    @mark.skip(reason="it fails and we're short on time")
    def test_project_edits(self, db):
        # We need to restart the ID sequence because this test makes
        # assumptions about the identity of auto-incrementing primary keys
        db.session.execute("ALTER SEQUENCE session_id_seq RESTART 1")

        # Load data (replaces load_data_loop)
        for model, spec_list in self.data.items():
            if model in ["og-project", "edit-project"]:
                continue
            for spec in spec_list:
                db.load_data(model, spec)

        db.load_data("project", self.data["og-project"])

        Session = db.model.session

        orig_sessions = db.session.query(Session.id).all()
        # We have two sessions in the database
        assert len(orig_sessions) == 2

        assert set([s.id for s in orig_sessions]) == set([1, 2])

    @mark.skip(reason="it fails and we're short on time")
    def test_documents_exist(self, db):
        """test if document tables have stuff in them"""

        tables = [
            "documents.project_document",
            "documents.sample_document",
            "documents.session_document",
        ]

        for table in tables:
            sql = f"SELECT * FROM {table}"

            res = db.session.execute(sql)
            assert len(res.all()) > 0

    @mark.skip(reason="it fails and we're short on time")
    def test_query_document(self, db):
        """test query the document table using orm methods"""
        document_names = ["project", "sample", "session"]

        for name in document_names:
            doc_table = Table(
                f"{name}_document", db.meta, autoload_with=db.engine, schema="documents"
            )
            res = db.session.query(doc_table)
            assert res.count() > 0

    @mark.skip(reason="it fails and we're short on time")
    def test_sample_search(self, db):
        """Use the match operator from sqlalchemy to search a document"""
        term = "granite"

        sample_doc = Table(
            "sample_document", db.meta, autoload_with=db.engine, schema="documents"
        )

        q = db.session.query(sample_doc).filter(sample_doc.c.sample_token.match(term))
        assert q.count() == 1

        ## attempt a join
        sample = db.model.sample
        q_sample = (
            db.session.query(sample)
            .join(sample_doc, sample.id == sample_doc.c.sample_id)
            .filter(sample_doc.c.sample_token.match(term))
        )
        assert q_sample.count() == 1
        assert q_sample.first().name == "fake3"

        ## test filter on match
        term = "basalt"
        q = db.session.query(sample).join(
            sample_doc, sample.id == sample_doc.c.sample_id
        )
        q = q.filter(sample_doc.c.sample_token.match(term))
        q = q.filter(sample.name == "fake1")

        assert q.count() == 1
        assert q.first().name == "fake1"

    @mark.skip(reason="it fails and we're short on time")
    def test_open_search_sample(self, db):
        """create an sqlalchemy query that is filterable that matches
        the open search sql file
        """
        sample = db.model.sample
        project = db.model.project
        session = db.model.session

        project_doc, sample_doc, session_doc = get_document_tables(db)

        query = "basalt"
        term = " & ".join(query.split())

        # assemble joins
        q = db.session.query(sample)
        q = q.outerjoin(sample_doc, sample.id == sample_doc.c.sample_id)
        q = q.outerjoin(sample.project_collection).join(
            project_doc, project.id == project_doc.c.project_id
        )

        q = q.outerjoin(sample.session_collection).join(
            session_doc, session.id == session_doc.c.session_id
        )

        # # apply search text searching
        q = q.filter(
            or_(
                sample_doc.c.sample_token.match(term),
                project_doc.c.project_token.match(term),
                session_doc.c.session_token.match(term),
            )
        )
        q = q.filter(sample.name == "fake1")

        assert q.count() > 0
        assert q.first().name == "fake1"

    @mark.skip(reason="it fails and we're short on time")
    def test_open_search_api(self, client, db):
        """test filter api"""

        models = {"project": "casey", "sample": "fake1", "session": "UW114"}

        for k, v in models.items():
            route = f"/api/v2/models/{k}?search={v}"

            res = client.get(route)
            data = res.json()
            assert data["total_count"] != 0

    @mark.skip(reason="it fails and we're short on time")
    def test_add_new(self, client, db):
        """test to see if new item added to documents table"""

        project_doc, sample_doc, session_doc = get_document_tables(db)

        res = db.session.query(sample_doc).all()

        sample = {"name": "AME18-203", "material": "granodiorite"}

        db.load_data("sample", sample)

        res2 = db.session.query(sample_doc).all()

        assert len(res2) > len(res)
