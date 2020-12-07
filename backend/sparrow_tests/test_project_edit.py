from .helpers import json_fixture
import json

class TestProjectEdits:
    '''
     Testing suite for the Project's edit API
    '''
    def test_import_dumpfile(self, db):
        data = json_fixture("project-doi-fixes.json")
        db.load_data("project", data["data"])

    def test_fix_doi(self, client, db):
        '''
         Try Deleting some of the bad DOI's

         How do I delete DOI's??

         First steps: make some changes to send to the put api
        '''
        Publications = db.model.publication
        pubs = db.session.query(Publications).all()

        route =  '/api/v2/project/edits?id=1'

        changes = {"id":1, "description": "Testing to add stuff", "publications": [{'id': 2, 'doi': '10.1016/j.quageo.2012.12.005'}]}
        changeset = json.dumps(changes)

        response = client.put(route, json = changeset)

    def test_delete_proj_pub_relationship(self, client, db):
        route = '/api/v2/project/edits?publication=6'

        response = client.delete(route)
        assert 0 ==1


    