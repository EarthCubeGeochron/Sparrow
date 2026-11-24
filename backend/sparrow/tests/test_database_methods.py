import pandas as pd
from macrostrat.database.utils import get_dataframe
from pytest import mark


def test_method_exec_query(db):
    data = get_dataframe(db.engine, "SELECT * FROM sample")
    assert data.columns[0] == "id"
