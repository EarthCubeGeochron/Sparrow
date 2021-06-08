from .helpers import json_fixture
from pytest import fixture, mark

@fixture(scope="class")
def test_projects(client, token):
    """Fixture to create a demo project"""
    data = json_fixture("projects-post.json")
    route = "/api/v2/models/project"
    res = client.post(route, headers={"Authorization":token},json=data)
    return res.json()["data"]

class TestModelPost:
    """
    Testing Suite to test the universal POST method on the api
    """
    route = "/api/v2/models/project" 

    def test_import_project(self, test_projects):
        """
        Test Importing some projects
        """
        assert len(test_projects) == 2

    def test_replace_project(self, client, test_projects, token):
        id = test_projects[0]["id"]
        route = f"{self.route}/{id}"
        new_project = json_fixture("new-project.json")
        res = client.post(route, headers={"Authorization":token},json=new_project)
        data = res.json()
        # Need to actually test something here....

    @mark.skip(reason="This clearly needs some work")
    def test_edit_researcher_in_project(self, client, test_projects, token):
        id = test_projects[0]["id"]
        edits = {"researcher": [{"name": "casey", "orcid": None}]}
        client.put(f"{self.route}/{id}", headers={"Authorization":token},json=edits)
        # assert res_put.status_code == 200
