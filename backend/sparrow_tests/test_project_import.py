from contextlib import redirect_stdout
from .helpers import json_fixture
from deepdiff import DeepDiff
from json import dumps, loads
from sparrow.core.encoders import JSONEncoder
from sqlalchemy import event
from sqlalchemy.orm import joinedload
from marshmallow import EXCLUDE
from datetime import datetime
from pytest import mark
import logging


def omit_key(changeset, key):
    return [k for k in changeset if not k.endswith(f"['{key}']")]


class TestProjectImport:
    def test_import_dumpfile(self, db, caplog):
        data = json_fixture("project-dump.json")
        # with caplog.at_level(logging.INFO, logger="sparrow.interface.schema"):
        #    # So we don't get spammed with output
        db.load_data("project", data["data"])

    def test_retrieve_dumpfile(self, db, caplog):
        data = json_fixture("project-dump.json")["data"]

        schema = db.interface.project(many=False, allowed_nests="all")
        res = db.session.query(schema.opts.model).filter_by(name=data["name"]).first()
        assert res is not None
        with caplog.at_level(logging.INFO, logger="sparrow.interface.schema"):
            out = loads(dumps(schema.dump(res), allow_nan=False, cls=JSONEncoder))
        assert len(out["session"]) == len(data["session"])

        assert out["session"][0]["uuid"] == data["session"][0]["uuid"]

        dd = DeepDiff(data, out)
        non_pk_changes = omit_key(dd["values_changed"], "id")
        assert len(non_pk_changes) == 0

        # In_plateau is not retained because that is added by the WiscAr lab
        # as a method-specific extension.
        removed = dd["dictionary_item_removed"]
        assert len(removed) > 0
        assert len(omit_key(removed, "in_plateau")) == 0

    def test_project_api_retreival(self, client):
        """Checks if models/sample is working"""
        res = client.get("/api/v2/models/project", params={"per_page": 1})
        assert res.status_code == 200
        res.json()

    def test_make_private(self, db):
        proj = db.session.query(db.model.project).first()
        proj.embargo_date = datetime.max
        db.session.add(proj)
        db.session.commit()

    def test_lazy_load(self, db, statements):
        assert len(statements) == 0  # Sanity check for fixture
        SampleSchema = db.interface.sample
        ss = SampleSchema(many=True, allowed_nests=["session", "analysis"])

        # First, do a "lazy load"
        res = db.session.query(ss.opts.model).all()
        assert len(res) > 0
        output = ss.dump(res)
        assert len(output) == len(res)
        assert len(statements) > len(res)
        # Don't keep objects around for later tests,
        # they will interfere with query counting because
        # cached session objects will be fetched instead
        db.session.expire_all()

    def test_joined_load(self, db, statements):
        """Test that we can do a joined load, which is important for
        rapidly assembling nested result sets (see API v2)."""
        SampleSchema = db.interface.sample
        ss = SampleSchema(many=True, allowed_nests=["session", "analysis"])
        q = db.session.query(ss.opts.model)
        joins = [joinedload(*arg) for arg in ss.nested_relationships()]
        q = q.options(*joins)
        res = q.all()

        assert len(res) > 0
        output = ss.dump(res)
        assert len(output) == len(res)
        assert len(statements) == 1

    @mark.xfail(reason="We need to figure out how to effectively overwrite data")
    def test_reimport_dumpfile(self, db):
        """We should be able to idempotently import a data file..."""
        data = json_fixture("project-dump.json")
        db.load_data("project", data["data"])
