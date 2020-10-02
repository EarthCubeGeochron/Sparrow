from sparrow.app import App
from sparrow.database.mapper import BaseModel
from marshmallow import Schema
from marshmallow.exceptions import ValidationError
from datetime import datetime
from pytest import mark
from sparrow.logs import get_logger

from .fixtures import basic_data, incomplete_analysis, basic_project
from .helpers import json_fixture, ensure_single

log = get_logger(__name__)


# pytestmark = mark.filterwarnings("ignore", "*", SAWarning)

# This should be in the fixture function ideally but I can't figure out
# how to cache it so it doesn't repeatedly regenerate.
app = App(__name__)

session = dict(sample_id="A-0", date=datetime.now())


class TestImperativeImport(object):
    def test_imperative_import(self, db):
        """
        Test importing some data using imperative SQLAlchemy. This is no
        longer the recommended approach (use import schemas instead). Many
        records must be inserted to successfully provide a single
        measured value, as can be seen below.

        Because this import method relies on fairly low-level SQLAlchemy
        code, it should work for more unusual import tasks that cannot be
        handled by the newer schema-based functionality.
        """
        authority = "Carolina Ag. Society"

        sample = db.get_or_create(db.model.sample, name="A-0")
        db.session.add(sample)
        db.session.flush()

        # Import a single session
        session = db.get_or_create(
            db.model.session,
            sample_id=sample.id,
            name="Imperative import test",
            date=datetime.now(),
        )
        db.session.add(session)

        # Analysis type
        a_type = db.get_or_create(
            db.model.vocabulary_analysis_type,
            id="Insect density inspection",
            authority=authority,
        )
        db.session.add(a_type)

        # Material
        mat = db.get_or_create(
            db.model.vocabulary_material, id="long-staple cotton", authority=authority
        )
        db.session.add(mat)

        # Analysis
        analysis = db.get_or_create(
            db.model.analysis,
            session_id=session.id,
            analysis_type=a_type.id,
            material=mat.id,
        )
        db.session.add(analysis)

        # Parameter
        param = db.get_or_create(
            db.model.vocabulary_parameter,
            authority=authority,
            id="weevil density",
            description="Boll weevil density",
        )
        db.session.add(param)

        # Unit
        unit = db.get_or_create(
            db.model.vocabulary_unit,
            id="insects/sq. decimeter",
            description="Insects per square decimeter",
            authority=authority,
        )
        db.session.add(unit)

        # Datum type
        type = db.get_or_create(db.model.datum_type, parameter=param.id, unit=unit.id)
        db.session.add(type)
        # not sure why we need to flush here...
        db.session.flush()

        # Parameter
        datum = db.get_or_create(
            db.model.datum, analysis=analysis.id, type=type.id, value=121, error=22
        )

        db.session.add(datum)
        db.session.commit()

    def test_import_successful(self, db):
        item = db.session.query(db.model.datum).first()
        assert item.value == 121
        assert item.error == 22

    def test_foreign_keys(self, db):
        item = db.session.query(db.model.session).first()
        assert item.sample_id is not None
        item = db.session.query(db.model.analysis).first()
        assert item.session_id is not None
        item = db.session.query(db.model.datum).first()
        assert item.analysis is not None
        assert item.type is not None

    def test_operation_log(self, db):
        """
        Test whether our PGMemento audit trail is working
        """

        res = db.session.execute("SELECT count(*) " "FROM pgmemento.table_event_log")
        total_ops = res.scalar()
        assert total_ops > 0

        res = db.session.execute(
            "SELECT table_operation, table_name "
            "FROM pgmemento.table_event_log "
            "ORDER BY id DESC LIMIT 1"
        )
        (op, tbl) = res.first()
        assert op == "INSERT"
        assert tbl == "datum"


class TestSchema:
    def test_basic_import(self, db):
        schema = db.interface.sample()
        name = "test sample"
        obj = {"name": name}
        inst = schema.load(obj, session=db.session, transient=True)
        assert inst.name == name
        res = schema.dump(inst)
        assert res["name"] == name

    def test_more_complex_import(self, db):
        schema = db.interface.session()
        inst = schema.load(basic_data, session=db.session, transient=True)
        res = schema.dump(inst)
        assert res["name"] == basic_data["name"]
        assert len(res["analysis"]) == 1

    def test_schema_structure(self, db):
        """
        Make sure that schemas follow basic conformance to their underlying
        SQLAlchemy models.
        """
        schema = db.interface.session()
        model = db.model.session()
        for k in schema.fields.keys():
            assert hasattr(model, k)

    def test_no_extra_unit_fields(self, db):
        """
        We had a problem with gratuitous extra nested fields being created.
        """
        schema = db.interface.vocabulary_unit()
        assert "sample_geo_entity_collection" not in schema.fields.keys()


class TestDeclarativeImporter:
    def test_import_interface(self, db):
        for model in ["datum", "session", "datum_type"]:
            iface = getattr(db.interface, model)
            assert isinstance(iface(), Schema)

    def test_standalone_sample(self, db):
        sample = {"name": "test sample 1"}
        db.load_data("sample", sample)
        db.load_data("sample", sample)
        ensure_single(db, "sample", **sample)

    def test_standalone_datum_type(self, db):
        data = {"parameter": "Oxygen fugacity", "unit": "dimensionless"}

        db.load_data("datum_type", data)
        # We should be able to import this idempotently
        db.load_data("datum_type", data)

    def test_basic_import(self, db):
        db.load_data("session", basic_data)
        ensure_single(db, "sample", name="Soil 001")

    def test_duplicate_import(self, db):
        db.load_data("session", basic_data)
        ensure_single(db, "sample", name="Soil 001")
        ensure_single(db, "session", name="Declarative import test")

    def test_duplicate_parameter(self, db):

        data = {
            "date": "2020-02-02T10:20:02",
            "name": "Declarative import test 2",
            "sample": {"name": "Soil 002"},
            "analysis": [
                {
                    "analysis_type": {"id": "Soil aliquot pyrolysis"},
                    "session_index": 0,
                    "datum": [
                        {
                            "value": 1.18,
                            "error": 0.15,
                            "type": {
                                "parameter": {"id": "soil water content"},
                                "unit": {"id": "weight %"},
                            },
                        }
                    ],
                }
            ],
        }

        db.load_data("session", data)

        ensure_single(db, "sample", name="Soil 002")
        ensure_single(db, "session", name="Declarative import test 2")

    def test_primary_key_loading(self, db):
        """We should be able to load already-existing values with their
        primary keys.
        """
        data = {
            "date": str(datetime.now()),
            "name": "Session primary key loading",
            "sample": {"name": "Soil 003"},
            "analysis": [
                {
                    "analysis_type": "Soil aliquot pyrolysis",
                    "session_index": 0,
                    "datum": [
                        {
                            "value": 0.280,
                            "error": 0.021,
                            "type": {
                                "parameter": "soil water content",
                                "unit": "weight %",
                            },
                        }
                    ],
                }
            ],
        }

        db.load_data("session", data)

    def test_session_merging(self, db):
        data = {
            "date": str(datetime.now()),
            "name": "Session merging test",
            "sample": {"name": "Soil 003"},
            "analysis": [
                {
                    # Can't seem to get or create this instance from the database
                    "analysis_type": {"id": "Soil aliquot pyrolysis"},
                    "session_index": 0,
                    "datum": [
                        {
                            "value": 0.252,
                            "error": 0.02,
                            "type": {
                                "parameter": {"id": "soil water content"},
                                "unit": {"id": "weight %"},
                            },
                        }
                    ],
                }
            ],
        }

        db.load_data("session", data)
        db.load_data("session", data)
        ensure_single(db, "session", name="Session merging test")
        ensure_single(db, "datum", value=0.252)

    def test_datum_type_merging(self, db):
        """Datum types should successfully find values already in the database.
        """
        ensure_single(db, "datum_type", parameter="soil water content", unit="weight %")

    def test_load_existing_instance(self, db):
        # Get an instance
        type = (
            db.session.query(db.model.datum_type)
            .filter_by(parameter="soil water content", unit="weight %", error_unit=None)
            .first()
        )

        assert type is not None
        assert isinstance(type, BaseModel)

        data = {
            "date": str(datetime.now()),
            "name": "Session with existing instances",
            "sample": {"name": "Soil 003"},
            "analysis": [
                {
                    # Can't seem to get or create this instance from the database
                    "analysis_type": "Soil aliquot pyrolysis",
                    "session_index": 0,
                    "datum": [{"value": 0.1, "error": 0.025, "type": type}],
                }
            ],
        }

        db.load_data("session", data)

    def test_get_instance(self, db):
        data = dict(parameter="soil water content", unit="weight %")
        dt = (
            db.session.query(db.model.datum_type)
            .filter_by(**data, error_unit=None)
            .first()
        )

        assert dt is not None

        res = db.get_instance("datum_type", data)

        assert isinstance(res, db.model.datum_type)
        assert res.id == dt.id

    def test_incomplete_import_excluded(self, db):
        try:
            db.load_data("analysis", incomplete_analysis)
            # We shouldn't succeed at importing this data
            assert False
        except Exception as err:
            assert isinstance(err, ValidationError)
            assert err.messages["session"][0] == "Missing data for required field."

    def test_duplicate_datum_type(self, db):

        data = {
            "date": str(datetime.now()),
            "name": "Session with existing instances",
            "sample": {"name": "Soil 003"},
            "analysis": [
                {
                    # Can't seem to get or create this instance from the database
                    "analysis_type": "Stable isotope analysis",
                    "session_index": 0,
                    "datum": [
                        {
                            "value": 0.1,
                            "error": 0.025,
                            "type": {"parameter": "delta 13C", "unit": "permille"},
                        }
                    ],
                },
                {
                    # Can't seem to get or create this instance from the database
                    "analysis_type": "Stable isotope analysis",
                    "session_index": 1,
                    "datum": [
                        {
                            "value": 0.2,
                            "error": 0.035,
                            "type": {"parameter": "delta 13C", "unit": "permille"},
                        }
                    ],
                },
            ],
        }

        db.load_data("session", data)

    def test_expand_id(self, caplog, db):
        # caplog.set_level(logging.INFO, "sqlalchemy.engine")

        data = {"parameter": "test param", "unit": "test unit"}
        val = db.load_data("datum_type", data)
        assert val._parameter.id == data["parameter"]
        assert val._unit.id == data["unit"]
        assert val._error_unit is None

    def test_get_number(self, db):
        res = db.get_instance("datum", dict(value=0.1, error=0.025))
        assert isinstance(res, db.model.datum)
        assert float(res.value) == 0.1

    @mark.skip
    def test_get_datum(self, db):
        res = db.get_instance("datum", dict(id=2))
        assert isinstance(res, db.model.datum)

    def test_import_instance_instead_of_list(self, db):
        """Do we get a meaningful error message if we import an instance rather
        than a list?"""

        invalid_project = dict(**basic_project)
        # The researcher model should be a collection, not an individual item.
        invalid_project["researcher"] = basic_project["researcher"][0]

        try:
            db.load_data("project", invalid_project)
            assert False  # Did not raise
        except ValidationError as err:
            assert (
                err.messages["researcher"][0]
                == "Provided a single object for a collection field"
            )


class TestStagedImport:
    @mark.xfail(reason="Need to update interface to support this.")
    def test_staged_import(self, db):
        """Test that we can import items with references to previously imported items"""
        sample = basic_data.pop("sample")
        session = db.load_data("session", basic_data)
        sample["session"] = [session]
        db.load_data("sample", sample)


class TestImportDataTypes(object):
    def test_simple_cosmo_import(self, db):
        # Test import of simple cosmogenic nuclides data types
        data = json_fixture("simple-cosmo-test.json")
        db.load_data("session", data)
