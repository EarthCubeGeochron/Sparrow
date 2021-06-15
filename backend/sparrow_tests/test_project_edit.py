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

   # @mark.xfail(reason="Updating does not work at the moment")
    def test_project_updates(self, db):
        # need a function like load_data but for edits..
        ## get interface and db model
        ProjectInterface = db.interface.project()

        nests = ProjectInterface._available_nests()

        inst = db.session.query(db.model.project).first()

        # get updates
        # data["edit-project"].pop("id")
        updates = self.data["edit-project"]

        # for k,v in updates.items():
        #     if k in nests:
        #         if type(v) is list:
        #             for id in v:



        sessions = db.session.query(db.model.session).all()
        samples = db.session.query(db.model.sample).all()
        publications= db.session.query(db.model.publication).all()

        assert 0 == 1


        # load updates into the project_schema and assign the same id as the existing
        new_proj = ProjectInterface.load(updates, session=db.session, instance=inst,partial=True)

        new_proj.session_collection = sessions
        new_proj.sample_collection = samples
        new_proj.publication_collection = publications
        
        new_proj.id = inst.id

        # NOTE: for some reason, i need to rollbakc before the merge.
        #       online examples don't need to do this
        # Merge the new_proj with the existing one in the session.
        db.session.rollback()

        res = db.session.merge(new_proj)
        # commit changes
        # seems to work well except for its creating an extra duplicate session.
        # it doesn't duplicate any other collection though.
        db.session.commit()

        assert db.session.query(db.model.project).count() == 1

        # the updates will have lengthened the publication collection
        project_test = db.session.query(db.model.project).get(new_proj.id)
        assert len(project_test.publication_collection) == 2
        # adding a new sample to the session.sample attribute creates a new session..
        sessions = db.session.query(db.model.session).all()
        assert len(sessions) == 2
