from .helpers import json_fixture
import json

def load_data_loop(model: str, data,db):
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

    def test_project_edits(self, db):
        data = json_fixture("project-edits.json")

        load_data_loop("publication", data['publication'], db)
        load_data_loop("researcher", data['researcher'], db)
        load_data_loop("sample", data['sample'], db)
        load_data_loop("session", data['session'], db)

        res = db.load_data("project", data["og-project"])

        # need a function like load_data but for edits..
        ## get interface and db model
        project_schema = db.interface.project()
        project = db.model.project

        # grab existing id and project
        proj_id = data['edit-project']['id']
        existing_project = project.query.get(proj_id)
        
        # get updates
        data['edit-project'].pop('id')
        updates = data['edit-project']

        # load updates into the project_schema and assign the same id as the existing
        new_proj = project_schema.load(updates, session=db.session, instance=existing_project)
        new_proj.id = existing_project.id

        # NOTE: for some reason, i need to rollbakc before the merge.
        #       online examples don't need to do this
        # Merge the new_proj with the existing one in the session.
        db.session.rollback()
        res = db.session.merge(new_proj)

        # commit changes
        # seems to work well except for its creating an extra duplicate session. 
        # it doesn't duplicate any other collection though.
        db.session.commit()
