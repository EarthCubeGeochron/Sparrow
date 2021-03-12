from .helpers import json_fixture
from pytest import mark
import json


def load_data_loop(model: str, data, db):
    for ele in data:
        db.load_data(model, ele)


class TestProjectEdits:
    """
    Testing suite for the Project's edit API
    Being re-factored to handle the project-admin page edits

    I need to load a bunch of data into the db.
    Then try sending edits to the project generated in the first step.

    https://marshmallow-sqlalchemy.readthedocs.io/en/latest/api_reference.html#marshmallow_sqlalchemy.SQLAlchemyAutoSchema
    https://stackoverflow.com/questions/31891676/update-row-sqlalchemy-with-data-from-marshmallow

    https://github.com/realpython/materials/blob/master/flask-connexion-rest-part-2/version_1/people.py
    """

    def test_isolation(self, db):
        sessions = db.session.query(db.model.session).all()
        assert len(sessions) == 0

    # @mark.skip  # xfail(reason="This is experimental")
    def test_project_edits(self, db):
        db.session.execute("ALTER SEQUENCE session_id_seq RESTART 1");

        data = json_fixture("project-edits.json")

        load_data_loop("publication", data["publication"], db)
        load_data_loop("researcher", data["researcher"], db)
        load_data_loop("sample", data["sample"], db)
        load_data_loop("session", data["session"], db)

        res = db.load_data("project", data["og-project"])

        # need a function like load_data but for edits..
        ## get interface and db model
        ProjectInterface = db.interface.project()

        Session = db.model.session

        orig_sessions = db.session.query(Session.id).all()
        # We have two sessions in the database
        assert len(orig_sessions) == 2

        # get updates
        data["edit-project"].pop("id")
        updates = data["edit-project"]

        # new_sessions = data["edit_project"].pop("session")
        # for sess, row in zip(new_sessions, orig_sessions):
        #     # Integrate database-provided IDs for existing sessions
        #     sess["id"] = row.id
        # updates["session"] = new_sessions

        # load updates into the project_schema and assign the same id as the existing
        new_proj = ProjectInterface.load(
            updates, session=db.session, instance=res, partial=True, transient=True
        )

        # NOTE: for some reason, i need to rollbakc before the merge.
        #       online examples don't need to do this
        # Merge the new_proj with the existing one in the session.
        # db.session.rollback()

        res = db.session.add(new_proj)

        # commit changes
        # seems to work well except for its creating an extra duplicate session.
        # it doesn't duplicate any other collection though.
        db.session.commit()

        # the updates will have lengthened the publication collection
        project_test = db.session.query(db.model.project).get(new_proj.id)
        assert len(project_test.publication_collection) == 3
        # adding a new sample to the session.sample attribute creates a new session..
        sessions = db.session.query(db.model.session).all()
        assert len(sessions) == 2
