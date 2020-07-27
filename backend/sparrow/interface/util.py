from stringcase import pascalcase


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
