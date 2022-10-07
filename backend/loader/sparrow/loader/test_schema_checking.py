from marshmallow import ValidationError
from pytest import raises
from . import show_loader_schemas, validate_data


def test_show_loader_schemas():
    show_loader_schemas()


def test_validate_data():
    validate_data("sample", {"name": "test"})


def test_validate_sample_with_no_name():
    with raises(ValidationError):
        validate_data("sample", {"nameza": None})
