from stringcase import pascalcase
#from marshmallow_sqlalchemy.fields import get_primary_keys
from sparrow.database.mapper.util import primary_key


def column_is_required(col):
    return all(
        [
            not col.nullable,  # Column cannot be null
            col.server_default is None,  # and has neither a database-side default
            col.default is None,  # nor an ORM default
        ]
    )


def to_schema_name(name):
    return pascalcase(name + "_schema")


def columns_for_prop(prop):
    try:
        return getattr(prop, "columns")
    except AttributeError:
        return list(getattr(prop, "local_columns"))


def prop_is_required(prop):
    cols = [column_is_required(c) for c in columns_for_prop(prop)]
    return any(cols)


def pk_values(instance):
    return primary_key(instance).values()


def pk_data(model, data):
    pk = primary_key(model)
    keys = {key: data.get(key) for key in pk.keys()}
    return keys.values()


def is_pk_defined(instance):
    vals = pk_values(instance)
    return all([v is not None for v in vals])