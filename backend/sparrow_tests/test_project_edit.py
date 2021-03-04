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
    """

    def test_import_dumpfile(self, db):
        data = json_fixture("project-edits.json")

        load_data_loop("publication", data['publication'], db)
        load_data_loop("researcher", data['researcher'], db)
        load_data_loop("sample", data['sample'], db)
        load_data_loop("session", data['session'], db)

        res = db.load_data("project", data["og-project"])

        # need a function like load_data but for edits..
        # can use interface stuff and use the make_instance. Does edits!
        project_schema = db.interface.project()
        proj_id = data['edit-project']['id']

        res = project_schema.load(data['edit-project'], session=db.session, instance = project_schema._get_instance(data['edit-project']))
        #db.load_data("project", data["edit-project"])
