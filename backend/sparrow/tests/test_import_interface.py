import json

from sqlalchemy.exc import IntegrityError
from sparrow.core.app import Sparrow
from sparrow.database.mapper import BaseModel
from marshmallow import Schema
from marshmallow.exceptions import ValidationError
from datetime import datetime
from pytest import mark, raises, fixture
from sparrow.logs import get_logger
from sparrow.core.encoders import JSONEncoder
from json import dumps
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from .fixtures import basic_data, incomplete_analysis, basic_project
from .helpers import json_fixture, ensure_single

log = get_logger(__name__)

# pytestmark = mark.filterwarnings("ignore", "*", SAWarning)

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

    @mark.skip(reason="There are more pressing matters...")
    def test_constant_session_fields(self, db):
        schema = db.interface.datum_type()
        assert "constant_collection" not in schema.fields.keys()


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

    def test_get_sample(self, db):
        """Can we get a sample by its ID?"""
        s = db.session.query(db.model.sample).filter_by(name="test sample 1").first()
        assert s is not None
        schema = db.interface.sample()
        res = schema.dump(s)
        assert res["session"] == []

    def test_standalone_datum_type(self, db):
        data = {"parameter": "Oxygen fugacity", "unit": "dimensionless"}

        db.load_data("datum_type", data)
        # We should be able to import this idempotently
        res = db.load_data("datum_type", data)
        assert res._error_unit is None

    def test_unit_creation(self, db):
        unit = "Yankovics / sq. meter"
        res = db.load_data("datum_type", {"parameter": "Weird density", "unit": unit})
        assert res.unit == unit
        assert res.error_unit is None

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

    def test_datum_type_accuracy(self, db):
        DatumType = db.model.datum_type
        res = (
            db.session.query(DatumType)
            .filter_by(parameter="soil water content", unit="weight %")
            .all()
        )
        assert len(res) == 1
        dt = res[0]
        assert dt.error_unit is None

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

    def test_datum_type_no_error_unit(self, db):
        """We haven't specified an error unit, so one should not be in the database"""
        DatumType = db.model.datum_type
        res = (
            db.session.query(DatumType)
            .filter_by(parameter="soil water content", unit="weight %")
            .all()
        )
        assert len(res) == 1
        dt = res[0]
        assert dt.error_unit is None

    def test_datum_type_merging(self, db):
        """Datum types should successfully find values already in the database."""
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

    def test_serialize_instance(self, db):
        """Make sure we can dump an instance to a JSON string"""
        inst = db.session.query(db.model.sample).first()
        SampleSchema = db.interface.sample()
        res = SampleSchema.dump(inst)
        dumps(res, cls=JSONEncoder)

    def test_get_instance_api(self, client):
        """Test that our API at least allows us to retrieve all of the data at once."""
        res = client.get("/api/v2/models/datum_type", params={"all": True})
        assert res.status_code == 200

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
        # Intermittently fails
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


class TestSampleMessages:
    sample = json_fixture("failing-sample-duplicates.json")

    def test_failing_sample_message(self, db):
        """Check to see whether a sample with an invalid duplicate key
        is rejected with an appropriate message"""
        try:
            db.load_data("sample", self.sample)
            assert False
        except IntegrityError as err:
            # We have an error from unique constraint violation
            exc = err.orig
            assert isinstance(exc, UniqueViolation)
            assert exc.diag.table_name == "datum"
            assert "duplicate key value violates unique constraint" in str(exc)
            assert "(analysis, type)" in str(exc)

    def test_fixed_sample_import(self, db):
        # Adjust sample to perform better by deduplicating length
        self.sample["session"][0]["analysis"][0]["datum"][2]["type"][
            "parameter"
        ] = "Length 2"
        db.load_data("sample", self.sample)


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


class TestIsolation:
    def test_isolation(self, db):
        sessions = db.session.query(db.model.session).all()
        assert len(sessions) == 0


class TestNestedQuerying:
    def test_nested_querying(self, db):
        SampleSchema = db.interface.sample
        ss = SampleSchema(allowed_nests=["session", "analysis"])
        relationships = ss.nested_relationships()
        assert len(relationships) >= 2
        for rel_list in relationships:
            for rel in rel_list:
                assert isinstance(rel.property, RelationshipProperty)


class TestStrictModeImport:
    def test_strict_mode_import(self, db):
        db.load_data("session", basic_data, strict=True)

    def test_strict_mode_import_fail(self, db):
        new_data = basic_data.copy()
        new_data["fancy"] = "so_fancy"
        with raises(ValidationError):
            db.load_data("session", new_data, strict=True)


class TestResearcherSampleImport:
    def test_duplicate_import(self, db):
        byrne = {"name": "David Byrne"}
        eno = {"name": "Brian Eno"}
        sample_data = [
            {"name": "Sample 1", "researcher": [byrne]},
            {"name": "Sample 2", "researcher": [byrne]},
            {"name": "Sample 3", "researcher": [byrne, eno]},
        ]

        for sample in sample_data:
            db.load_data("sample", sample, strict=True)

        db.session.commit()

        assert db.session.query(db.model.researcher).count() == 2

    def test_same_researcher_import(self, db):
        """Re-importing the same researcher should lead to no change"""
        byrne = {"name": "David Byrne"}

        db.load_data("researcher", byrne, strict=True)
        assert db.session.query(db.model.researcher).count() == 2

    def test_researcher_orcid_import(self, db):
        """Re-importing the same researcher with a new orcid should add a new researcher."""
        byrne = {"name": "David Byrne", "orcid": "0000-0002-1825-0097"}

        db.load_data("researcher", byrne, strict=True)
        assert db.session.query(db.model.researcher).count() == 3


class TestResearcherProjectImport:
    projects = [
        {"name": "Project 1", "researcher": [{"name": "David Byrne"}]},
        {"name": "Project 2", "researcher": [{"name": "David Byrne"}]},
    ]

    def test_researcher_project_import(self, db):
        """Re-importing the same researcher with a new project should keep the same researcher."""

        for project in self.projects:
            db.load_data("project", project, strict=True)

        assert db.session.query(db.model.project).count() == 2
        assert db.session.query(db.model.researcher).count() == 1

    def test_change_researcher(self, db):
        # Re-import as a single operation (trying out many at once)
        project = self.projects[0]
        project["researcher"] = [{"name": "Brian Eno"}]

        db.load_data("project", project, strict=True)

        assert db.session.query(db.model.project).count() == 2
        assert db.session.query(db.model.researcher).count() == 2

        # Next: check for moved files


@fixture()
def new_analysis_data(db):
    session = json_fixture("sims-session.json")
    res = db.load_data("session", session)
    return {
        "session": res,
        "analysis_type": "Grain dimensions",
        "datum": [
            {"type": {"parameter": "Length", "unit": "µm"}, "value": 1.0},
            {"type": {"parameter": "Width", "unit": "µm"}, "value": 2.0},
        ],
    }


class TestAddToExisting:
    def test_add_session_existing_sample(self, db):
        """Test that we can add to an existing session"""
        sample = db.load_data(
            "sample",
            {
                "name": "Sample 1",
                "session": [{"name": "Test session", "date": "2022-01-01T00:00:00"}],
            },
        )

        db.load_data(
            "session",
            {"sample": sample, "name": "Test session 2", "date": "2022-01-02T00:00:00"},
        )

    def test_add_analysis_existing_session(self, db, new_analysis_data):
        """Test that we can add to an existing session"""

        db.load_data("analysis", new_analysis_data, strict=True)

    def test_extend_analysis_without_existing_values(self, db):
        start_count = db.session.query(db.model.analysis).count()
        datum_count = db.session.query(db.model.datum).count()
        analysis = db.session.query(db.model.analysis).first()

        new_datum = {
            "type": {"parameter": "Roundness", "unit": "dimensionless"},
            "value": 0.88,
            "analysis": analysis,
        }

        datum = db.load_data("datum", new_datum, strict=True)

        assert datum._analysis == analysis

        assert db.session.query(db.model.analysis).count() == start_count
        assert db.session.query(db.model.datum).count() == datum_count + 1

    @mark.skip(
        "This creates a new analysis right now, rather than updating the current instance."
    )
    def test_replace_data_for_existing_analysis(self, db, new_analysis_data):
        """Here, we replace all the data with a new set."""

        datum_count = db.session.query(db.model.datum).count()

        analysis = db.session.query(db.model.analysis).first()

        new_analysis_data["datum"][0]["value"] = 3.0

        new_analysis = db.load_data(
            "analysis", new_analysis_data, strict=True, instance=analysis
        )

        assert db.session.query(db.model.analysis).count() == 1
        assert db.session.query(db.model.datum).count() == datum_count
        assert len(new_analysis._datum) == 3
        assert new_analysis._datum[0].value == 4.0

    @mark.skip(
        "This creates a new analysis right now, rather than updating the current instance."
    )
    def test_extend_analysis_with_new_datum(self, db):
        datum_count = db.session.query(db.model.datum).count()
        analysis_count = db.session.query(db.model.analysis).count()
        analysis = db.session.query(db.model.analysis).first()

        new_datum = {"type": {"parameter": "Thickness", "unit": "nm"}, "value": 5.0}
        new_analysis_data["datum"].append(new_datum)
        new_analysis = db.load_data(
            "analysis", new_analysis_data, strict=True, instance=analysis
        )

        assert db.session.query(db.model.analysis).count() == analysis_count
        assert db.session.query(db.model.datum).count() == datum_count + 1
        assert len(new_analysis._datum) == 4
        assert new_analysis._datum[3].value == 5.0


class TestImportDates:
    def test_import_date_iso8601(self, db):
        """Test that we can import dates in ISO 8601 format"""
        date = {
            "name": "Test date",
            "date": "2022-01-01T00:00:00",
            "sample": {"name": "Sample 1"},
        }
        db.load_data("session", date, strict=True)

    def test_import_date_no_time(self, db):
        """Test that we can import a basic date"""
        date = {
            "name": "Test date",
            "date": "2022-01-01",
            "sample": {"name": "Sample 1"},
        }
        db.load_data("session", date, strict=True)

    def test_import_python_datetime(self, db):
        """Test that we can import a python datetime object"""
        date = datetime(2022, 2, 1)
        session = {"name": "Test date", "date": date, "sample": {"name": "Sample 1"}}
        db.load_data("session", session, strict=True)
