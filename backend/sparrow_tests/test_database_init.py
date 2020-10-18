from datetime import datetime
from pytest import mark
from sparrow.logs import get_logger
from sqlalchemy.engine.reflection import Inspector
import numpy as N

log = get_logger(__name__)

# pytestmark = mark.filterwarnings("ignore", "*", SAWarning)

session = dict(sample_id="A-0", date=datetime.now())


class TestDB:
    def test_standalone_datum_type(self, db):
        """Load a simple data type"""
        data = {"parameter": "Oxygen fugacity1", "unit": "dimensionless"}
        db.load_data("datum_type", data)


class TestDBRollback:
    def test_rollback(self, db):
        results = db.session.query(db.model.datum_type).all()
        log.debug(results)
        assert len(results) == 0


class TestDatabaseInitialization:
    core_automapped_tables = [
        "enum_date_precision",
        "instrument",
        "publication",
        "sample",
        "vocabulary_material",
        "vocabulary_method",
        "vocabulary_error_metric",
        "vocabulary_unit",
        "vocabulary_parameter",
        "analysis",
        "vocabulary_analysis_type",
        "constant",
        "researcher",
        "data_file",
        "data_file_type",
        "attribute",
        "data_file_link",
        "datum",
        "user",
        "project",
        "session",
        "datum_type",
        "vocabulary_entity_type",
        "vocabulary_entity_reference",
        "geo_entity",
        "sample_geo_entity",
        "core_view_datum",
    ]

    def test_db_automap(self, db):
        """
        Make sure that all core tables are automapped by the
        SQLAlchemy mapper.
        """
        for t in self.core_automapped_tables:
            assert t in db.model.keys()

    def test_constraint_finding(self, db):
        insp = Inspector.from_engine(db.engine)
        unique = insp.get_unique_constraints("session")
        for c in unique:
            # Find column constraint for uuid
            if len(c["column_names"]) == 1 and c["column_names"][0] == "uuid":
                assert True
                return
        assert False

    def test_db_automap_constraints(self, db):
        session = db.model.session
        uuid = session.uuid.prop
        assert uuid.columns[0].unique

    def test_db_interface(self, db):
        """
        Make sure all mapped tables have an import interface attached
        """
        for t in self.core_automapped_tables:
            if t in ("enum_date_precision", "core_view_datum"):
                continue
            assert t in db.interface.keys()

    def test_interface_ready(self, db):
        for iface in db.interface:
            iface()


class TestGenericData(object):
    @mark.xfail(reason="'get_instance' has a poorly written API.")
    def test_get_instance(self, db):
        sample = db.get_instance("sample", {"name": "Nonexistent sample"})
        assert sample is None


class TestGeoInstance(object):
    obj = {
        "name": "Test sample",
        "location": {"type": "Point", "coordinates": [122, 35.225]},
    }

    def test_geo_object_creation(self, db):
        inst = db.load_data("sample", self.obj)
        assert inst is not None
        schema = db.model_schema("sample")

        out = schema.dump(inst)
        assert out["location"] is not None
        c0 = self.obj["location"]["coordinates"]
        c1 = out["location"]["coordinates"]
        assert N.allclose(c0, c1)
