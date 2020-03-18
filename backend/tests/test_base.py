from sparrow.app import construct_app
from sparrow.util import relative_path
from sparrow.database.mapper import BaseModel
from marshmallow.exceptions import ValidationError
from sqlalchemy import and_
from datetime import datetime
from pytest import mark, fixture
import logging
from json import load

app, db = construct_app()

session = dict(
    sample_id="A-0",
    date=datetime.now())

logging.basicConfig(level=logging.CRITICAL)

class TestImperativeImport:
    def test_imperative_import(self):
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

        sample = db.get_or_create(
            db.model.sample,
            name="A-0")
        db.session.add(sample)
        db.session.flush()

        # Import a single session
        session = db.get_or_create(
            db.model.session,
            sample_id=sample.id,
            name="Imperative import test",
            date=datetime.now())
        db.session.add(session)

        # Analysis type
        a_type = db.get_or_create(
            db.model.vocabulary_analysis_type,
            id="Insect density inspection",
            authority=authority)
        db.session.add(a_type)

        # Material
        mat = db.get_or_create(
            db.model.vocabulary_material,
            id="long-staple cotton",
            authority=authority)
        db.session.add(mat)

        # Analysis
        analysis = db.get_or_create(
            db.model.analysis,
            session_id=session.id,
            analysis_type=a_type.id,
            material=mat.id)
        db.session.add(analysis)

        # Parameter
        param = db.get_or_create(
            db.model.vocabulary_parameter,
            authority=authority,
            id="weevil density",
            description="Boll weevil density")
        db.session.add(param)

        # Unit
        unit = db.get_or_create(
            db.model.vocabulary_unit,
            id="insects/sq. decimeter",
            description="Insects per square decimeter",
            authority=authority)
        db.session.add(unit)

        # Datum type
        type = db.get_or_create(
            db.model.datum_type,
            parameter=param.id,
            unit=unit.id)
        db.session.add(type)
        # not sure why we need to flush here...
        db.session.flush()

        # Parameter
        datum = db.get_or_create(
            db.model.datum,
            analysis=analysis.id,
            type=type.id,
            value=121,
            error=22)

        db.session.add(datum)
        db.session.commit()

    def test_import_successful(self):
        item = db.session.query(db.model.datum).first()
        assert item.value == 121
        assert item.error == 22

    def test_foreign_keys(self):
        item = db.session.query(db.model.session).first()
        assert item.sample_id is not None
        item = db.session.query(db.model.analysis).first()
        assert item.session_id is not None
        item = db.session.query(db.model.datum).first()
        assert item.analysis is not None
        assert item.type is not None

    def test_operation_log(self):
        """
        Test whether our PGMemento audit trail is working
        """
        res = db.session.execute("SELECT count(*) "
                                 "FROM pgmemento.table_event_log")
        total_ops = res.scalar()
        assert total_ops > 0

        res = db.session.execute("SELECT table_operation, table_name "
                                 "FROM pgmemento.table_event_log "
                                 "ORDER BY id DESC LIMIT 1")
        (op, tbl) = res.first()
        assert op == "INSERT"
        assert tbl == "datum"

basic_data = {
    "date": str(datetime.now()),
    "name": "Declarative import test",
    "sample": {
        "name": "Soil 001"
    },
    "analysis": [{
        "analysis_type": {
            "id": "Soil aliquot pyrolysis",
            "description": "I guess this could be an actual technique?"
        },
        "session_index": 0,
        "datum": [{
            "value": 2.25,
            "error": 0.2,
            "type": {
                "parameter": {
                    "id": "soil water content"
                },
                "unit": {
                    "id": "weight %"
                }
            }
        }]
    }]
}

def ensure_single(model_name, **filter_params):
    model = getattr(db.model, model_name)
    n = db.session.query(model).filter_by(**filter_params).count()
    assert n == 1

class TestDeclarativeImporter:
    def test_import_interface(self):
        for model in ['datum', 'session', 'datum_type']:
            assert hasattr(db.interface, model)

    def test_standalone_sample(self):
        sample = {'name': 'test sample 1'}
        db.load_data("sample", sample)
        db.load_data("sample", sample)
        ensure_single('sample', **sample)

    def test_standalone_datum_type(self):
        data = {
            "parameter": "Oxygen fugacity",
            "unit": "dimensionless"
        }

        db.load_data("datum_type", data)
        # We should be able to import this idempotently
        db.load_data("datum_type", data)

    def test_basic_import(self):
        db.load_data("session", basic_data)
        ensure_single('sample', name="Soil 001")

    def test_duplicate_import(self):
        db.load_data("session", basic_data)
        ensure_single('sample', name="Soil 001")
        ensure_single('session', name="Declarative import test")

    def test_duplicate_parameter(self):

        data = {
            "date": "2020-02-02T10:20:02",
            "name": "Declarative import test 2",
            "sample": {
                "name": "Soil 002"
            },
            "analysis": [{
                "analysis_type": {
                    "id": "Soil aliquot pyrolysis"
                },
                "session_index": 0,
                "datum": [{
                    "value": 1.18,
                    "error": 0.15,
                    "type": {
                        "parameter": {
                            "id": "soil water content"
                        },
                        "unit": {
                            "id": "weight %"
                        }
                    }
                }]
            }]
        }

        db.load_data("session", data)

        ensure_single('sample', name="Soil 002")
        ensure_single('session', name="Declarative import test 2")

    def test_primary_key_loading(self):
        """We should be able to load already-existing values with their
        primary keys.
        """
        data = {
            "date": str(datetime.now()),
            "name": "Session primary key loading",
            "sample": {
                "name": "Soil 003"
            },
            "analysis": [{
                "analysis_type": "Soil aliquot pyrolysis",
                "session_index": 0,
                "datum": [{
                    "value": 0.280,
                    "error": 0.021,
                    "type": {
                        "parameter": "soil water content",
                        "unit": "weight %"
                    }
                }]
            }]
        }

        db.load_data("session", data)

    def test_session_merging(self):
        data = {
            "date": str(datetime.now()),
            "name": "Session merging test",
            "sample": {
                "name": "Soil 003"
            },
            "analysis": [{
                # Can't seem to get or create this instance from the database
                "analysis_type": {
                    "id": "Soil aliquot pyrolysis"
                },
                "session_index": 0,
                "datum": [{
                    "value": 0.252,
                    "error": 0.02,
                    "type": {
                        "parameter": {
                            "id": "soil water content"
                        },
                        "unit": {
                            "id": "weight %"
                        }
                    }
                }]
            }]
        }

        db.load_data("session", data)
        db.load_data("session", data)
        ensure_single("session", name="Session merging test")
        ensure_single("datum", value=0.252)

    #@mark.skip(reason="Intermittent failure due to incorrect 'error_unit' setting")
    def test_datum_type_merging(self):
        """Datum types should successfully find values already in the database.
        """
        ensure_single("datum_type", parameter='soil water content', unit='weight %')

    def test_load_existing_instance(self):
        # Get an instance
        type = db.session.query(db.model.datum_type).filter_by(
            parameter='soil water content',
            unit='weight %',
            error_unit=None).first()

        assert isinstance(type, BaseModel)

        data = {
            "date": str(datetime.now()),
            "name": "Session with existing instances",
            "sample": {
                "name": "Soil 003"
            },
            "analysis": [{
                # Can't seem to get or create this instance from the database
                "analysis_type": "Soil aliquot pyrolysis",
                "session_index": 0,
                "datum": [{
                    "value": 0.1,
                    "error": 0.025,
                    "type": type
                }]
            }]
        }

        db.load_data("session", data)

    def test_incomplete_import_excluded(self):
        # Get an instance
        type = db.session.query(db.model.datum_type).filter_by(
            parameter='soil water content',
            unit='weight %',
            error_unit=None).first()

        assert isinstance(type, BaseModel)

        data = {
            # Can't seem to get or create this instance from the database
            "analysis_type": "Soil aliquot pyrolysis",
            "session_index": 0,
            "datum": [{
                "value": 0.1,
                "error": 0.025,
                "type": {
                    'parameter': 'soil water content',
                    'unit': 'weight %'
                }
            }]
        }

        try:
            db.load_data("analysis", data)
        except Exception as err:
            assert isinstance(err, ValidationError)

    def test_duplicate_datum_type(self):

        data = {
            "date": str(datetime.now()),
            "name": "Session with existing instances",
            "sample": {
                "name": "Soil 003"
            },
            "analysis": [{
                # Can't seem to get or create this instance from the database
                "analysis_type": "Stable isotope analysis",
                "session_index": 0,
                "datum": [{
                    "value": 0.1,
                    "error": 0.025,
                    "type": {
                        'parameter': 'delta 13C',
                        'unit': 'permille'
                    }
                }]
            }, {
                # Can't seem to get or create this instance from the database
                "analysis_type": "Stable isotope analysis",
                "session_index": 1,
                "datum": [{
                    "value": 0.2,
                    "error": 0.035,
                    "type": {
                        'parameter': 'delta 13C',
                        'unit': 'permille'
                    }
                }]
            }]
        }

        db.load_data("session", data)

    #@mark.skip(reason="Intermittent failure due to incorrect 'error_unit' setting")
    def test_expand_id(self, caplog):
        caplog.set_level(logging.INFO, 'sqlalchemy.engine')

        data = {'parameter': 'test param', 'unit': 'test unit'}
        val = db.load_data("datum_type", data)
        assert val._parameter.id == data['parameter']
        assert val._unit.id == data['unit']
        assert val._error_unit is None

    def test_get_instance(self):
        q = {
            'parameter': 'soil water content',
            'unit': 'weight %'
        }
        type = db.session.query(db.model.datum_type).filter_by(
            parameter=q['parameter'],
            unit=q['unit'],
            error_unit=None).first()

        res = db.get_instance('datum_type', q)

        assert isinstance(res, db.model.datum_type)
        assert res.id == type.id

    def test_get_number(self):
        res = db.get_instance('datum', dict(value=0.1, error=0.025))
        assert isinstance(res, db.model.datum)
        assert float(res.value) == 0.1

    @mark.skip
    def test_get_datum(self):
        res = db.get_instance('datum', dict(id=2))
        assert isinstance(res, db.model.datum)

@fixture
def client():
    with app.test_client() as client:
        yield client

data0 = {
  "filename": None,
  "data": {
    "name": "Test session 1",
    "sample": {
      "name": "Test sample"
    },
    "date": "2020-01-01T00:00:00",
    "analysis": [
      {
        "analysis_type": "d18O measurement trial",
        "datum": [
          {
            "value": 9.414,
            "type": {
              "parameter": "d18Omeas",
              "unit": "permille"
            }
          }
        ]
      }
    ]
  }
}

class TestAPIImporter:
    def test_api_import(self, client):
        res = client.put("/api/v1/import-data/session", json={'filename': None, 'data': basic_data})
        assert res.status_code == 201

    def test_basic_import(self, client):
        res = client.put("/api/v1/import-data/session", json=data0)
        assert res.status_code == 201

    @mark.skip
    def test_complex_single_row_prior(self, client):
        # This test fails if before the overall import
        # Too much output
        #logging.disable(logging.CRITICAL)

        fn = relative_path(__file__, 'large-test.json')
        with open(fn) as fp:
            complex_data = load(fp)
        complex_data['data']['analysis'] = complex_data['data']['analysis'][2:3]

        db.load_data("session", complex_data['data'])

    def test_complex_import(self, client):
        # Too much output
        logging.disable(logging.DEBUG)

        fn = relative_path(__file__, 'large-test.json')
        with open(fn) as fp:
            complex_data = load(fp)

        db.load_data("session", complex_data['data'])

        a = db.model.analysis
        q = db.session.query(a).filter(and_(a.session_index != None,
                                            a.analysis_type == 'd18O measurement'))
        assert q.count() > 1

    def test_complex_single_row(self, client):
        # This test fails if before the overall import
        # Too much output
        #logging.disable(logging.CRITICAL)

        fn = relative_path(__file__, 'large-test.json')
        with open(fn) as fp:
            complex_data = load(fp)
        complex_data['data']['analysis'] = complex_data['data']['analysis'][3:4]

        db.load_data("session", complex_data['data'])