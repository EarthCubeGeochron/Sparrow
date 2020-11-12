import pandas as pd
from pytest import mark


def test_method_exec_query(db):
    data = db.exec_query("SELECT * FROM vocabulary.metrics")
    assert data.columns[0] == 'samples_with_location'