from marshmallow import ValidationError
from pytest import raises
from datetime import datetime
from . import show_loader_schemas, validate_data


def test_show_loader_schemas():
    show_loader_schemas()


def test_show_single_schema():
    show_loader_schemas("sample")


def test_validate_data():
    validate_data("sample", {"name": "test"})


def test_validate_sample_with_no_name():
    with raises(ValidationError):
        validate_data("sample", {"nameza": None})


def test_validate_complex_sample():
    test_data = {
        "date": str(datetime.now()),
        "name": "Session with existing instances",
        "sample": {"name": "Test sample"},
        "analysis": [
            {
                # Can't seem to get or create this instance from the database
                "analysis_type": "Stable isotope analysis",
                "session_index": 0,
                "datum": [
                    {
                        "value": 0.1,
                        "error": 0.025,
                        "type": {
                            # Missing field "parameter" here!
                            "unit": "permille"
                        },
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
    validate_data("session", test_data)
