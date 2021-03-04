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
        project_schema = db.interface.project()
        project = db.model.project
        proj_id = data['edit-project']['id']

        existing_project = project.query.get(proj_id)
        
        data['edit-project'].pop('id')
        updates = data['edit-project']

        new_proj = project_schema.load(updates, session=db.session, instance=existing_project)
        new_proj.id = existing_project.id

        db.session.rollback()
        res = db.session.merge(new_proj)
        db.session.commit()
