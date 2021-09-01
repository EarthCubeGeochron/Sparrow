from .helpers import json_fixture
from pytest import mark, fixture
import json


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

    data = json_fixture("project-edits.json")

    def test_isolation(self, db):
        assert db.session.query(db.model.project).count() == 0
        sessions = db.session.query(db.model.session).all()
        assert len(sessions) == 0

    # @mark.skip  # xfail(reason="This is experimental")
    def test_project_edits(self, db):
        # We need to restart the ID sequence because this test makes
        # assumptions about the identity of auto-incrementing primary keys
        db.session.execute("ALTER SEQUENCE session_id_seq RESTART 1")

        # Load data (replaces load_data_loop)
        for model, spec_list in self.data.items():
            if model in [
                "og-project",
                "edit-project",
                "geojson",
                "wkt",
                "schema-sample-wkt",
                "schema-sample-geojson",
            ]:
                continue
            for spec in spec_list:
                db.load_data(model, spec)

        db.load_data("project", self.data["og-project"])

        Session = db.model.session

        orig_sessions = db.session.query(Session.id).all()
        # We have two sessions in the database
        assert len(orig_sessions) == 2

        assert set([s.id for s in orig_sessions]) == set([1, 2])

    def test_add_location(self, db):
        """ geojson geometry must be passed """
        sample = db.model.sample

        sample_ = db.session.query(sample).first()

        assert sample_.location is None

        loc = self.data["wkt"]

        sample_.location = loc
        assert len(db.session.dirty) > 0

        db.session.commit()

        sample_2 = db.session.query(sample).get(sample_.id)

        assert sample_2.location is not None

        Sample = db.interface.sample()

        sample_geojson = self.data["schema-sample-geojson"]

        samp = Sample.load(sample_geojson, session=db.session)

        assert samp.location is not None

    @mark.xfail(reason="Updating does not work at the moment")
    def test_project_updates(self, db):
        # need a function like load_data but for edits..
        ## get interface and db model
        ProjectInterface = db.interface.project()

        # get updates
        # data["edit-project"].pop("id")
        updates = self.data["edit-project"]

        inst = db.session.query(db.model.project).first()
        updates["id"] = inst.id

        # new_sessions = data["edit_project"].pop("session")
        # for sess, row in zip(new_sessions, orig_sessions):
        #     # Integrate database-provided IDs for existing sessions
        #     sess["id"] = row.id
        # updates["session"] = new_sessions

        # We aren't good at merging in changes to samples
        # If we don't delete this, the test fails!
        del updates["session"][0]["sample"]

        # load updates into the project_schema and assign the same id as the existing
        new_proj = ProjectInterface.load(updates, session=db.session, partial=True)

        # NOTE: for some reason, i need to rollbakc before the merge.
        #       online examples don't need to do this
        # Merge the new_proj with the existing one in the session.
        # db.session.rollback()

        res = db.session.merge(new_proj)
        # commit changes
        # seems to work well except for its creating an extra duplicate session.
        # it doesn't duplicate any other collection though.
        db.session.commit()

        assert db.session.query(db.model.project).count() == 1

        # the updates will have lengthened the publication collection
        project_test = db.session.query(db.model.project).get(new_proj.id)
        assert len(project_test.publication_collection) == 3
        # adding a new sample to the session.sample attribute creates a new session..
        sessions = db.session.query(db.model.session).all()
        assert len(sessions) == 2
