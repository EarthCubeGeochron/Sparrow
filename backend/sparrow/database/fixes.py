from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.ext import automap

def _is_many_to_many(automap_base, table):
    """
    Version of `sqlalchemy.ext.automap._is_many_to_many` function that ignores
    the `audit_id` column in the detection of "secondary" models for many-to-many
    relationships. Preserves near-default SQLAlchemy automapping behavior,
    ignoring extra metadata columns.
    """
    # Note: ideally this would be defined in the 'versioning' plugin but that currently
    # isn't loaded during import...

    fk_constraints = [const for const in table.constraints
                      if isinstance(const, ForeignKeyConstraint)]

    if len(fk_constraints) != 2:
        return None, None, None

    cols = sum(
        [[fk.parent for fk in fk_constraint.elements]
         for fk_constraint in fk_constraints], [])

    # Patch columns to ignore audit_id in calculation of number of columns
    # (only ForeignKey columns should be defined in order to
    #  establish this as a secondary model)
    if set(cols) != set([c for c in table.c if c.name != 'audit_id']):
        return None, None, None

    return (
        fk_constraints[0].elements[0].column.table,
        fk_constraints[1].elements[0].column.table,
        fk_constraints
    )

# Apply the hotfix to the SQLAlchemy model.
automap._is_many_to_many = _is_many_to_many
