import pandas as pd
from pytest import mark
from macrostrat.database.utils import get_dataframe


def test_method_exec_query(db):
    data = get_dataframe(db.engine, "SELECT * FROM sample")
    assert data.columns[0] == "id"
