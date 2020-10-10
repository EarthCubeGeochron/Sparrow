from .helpers import json_fixture
from deepdiff import DeepDiff
from json import dumps, loads
from sparrow.encoders import JSONEncoder


def omit_key(changeset, key):
    return [k for k in changeset if not k.endswith(f"['{key}']")]


class TestProjectImport:
    def test_import_dumpfile(self, db):
        data = json_fixture("project-dump.json")
        db.load_data("project", data["data"])

    def test_retrieve_dumpfile(self, db):
        data = json_fixture("project-dump.json")["data"]

        schema = db.interface.project(many=False, allowed_nests="all")
        res = db.session.query(schema.opts.model).filter_by(name=data["name"]).first()
        assert res is not None
        out = loads(dumps(schema.dump(res), allow_nan=False, cls=JSONEncoder))
        assert len(out["session"]) == len(data["session"])

        dd = DeepDiff(data, out)
        non_pk_changes = omit_key(dd["values_changed"], "id")
        assert len(non_pk_changes) == 0

        # In_plateau is not retained because that is added by the WiscAr lab
        # as a method-specific extension.
        removed = dd["dictionary_item_removed"]
        assert len(removed) > 0
        assert len(omit_key(removed, "in_plateau")) == 0