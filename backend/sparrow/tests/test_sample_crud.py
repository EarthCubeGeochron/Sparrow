from datetime import datetime
from sqlalchemy.exc import ProgrammingError
from psycopg2.errors import InsufficientPrivilege


class TestSampleCRUD:
    def test_sample_loading(self, db):
        """We should be able to load already-existing values with their
        primary keys.
        """
        data = {
            "name": "Soil 003",
            "location": {"type": "Point", "coordinates": [-5, 5]},
            "sessions": [
                {
                    "date": str(datetime.now()),
                    "name": "Session primary key loading",
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
                            "attributes": [
                                {"name": "Soil horizon", "value": "A"},
                                {"name": "Soil depth range", "value": "0-10 cm"},
                            ],
                        }
                    ],
                    "attributes": [
                        {"name": "Operator", "value": "Wendy Sørensen"},
                        {"name": "Operation mode", "value": "Vacuum stabilization"},
                    ],
                    "instrument": {"name": "Postnova AF2000"},
                }
            ],
            "attributes": [
                {"name": "Soil type", "value": "Sandy loam"},
                {"name": "Soil horizon", "value": "A"},
                {"name": "Soil depth range", "value": "0-10 cm"},
            ],
        }

        db.load_data("sample", data)

    def test_sample_deletion_unauthorized(self, db):
        """We should not be able to delete a sample without the right permissions."""

        db.session.execute("SET ROLE 'view_public'")
        Sample = db.model.sample
        model = db.session.query(Sample).filter_by(name="Soil 003").one()
        try:
            db.session.delete(model)
        except ProgrammingError as err:
            assert isinstance(err.orig, InsufficientPrivilege)
            assert "permission denied for table sample" in str(err.orig)

    def test_sample_deletion(self, db):
        """We should be able to delete a sample and all associated data."""
        db.session.rollback()
        Sample = db.model.sample
        model = db.session.query(Sample).filter_by(name="Soil 003").one()
        db.session.delete(model)
