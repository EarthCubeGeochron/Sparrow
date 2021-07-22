from sparrow_tests.helpers import json_fixture


class TestOpenSearch:
    """
    A testing suite to build upon the
    open search functionality.

    """

    data = json_fixture("project-edits.json")

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

    def test_documents_exist(self, db):
        """"""
        tables = [
            "documents.project_document",
            "documents.sample_document",
            "documents.session_document",
        ]

        for table in tables:
            sql = f"SELECT * FROM {table}"

            res = db.session.execute(sql)
            assert len(res.all()) > 0
