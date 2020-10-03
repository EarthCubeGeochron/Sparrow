from .helpers import json_fixture


class TestProjectImport:
    def test_import_dumpfile(self, db):
        data = json_fixture("project-dump.json")
        db.load_data("project", data["data"])
