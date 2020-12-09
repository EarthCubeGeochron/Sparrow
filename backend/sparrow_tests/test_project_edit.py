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

        route =  '/api/v2/project/edit/1'
        changeset = json_fixture("project-edits.json")

        response = client.put(route, json = changeset)

        assert 0 == 1


    