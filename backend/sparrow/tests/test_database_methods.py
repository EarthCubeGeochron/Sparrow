from sqlalchemy import text


def test_method_exec_query(db):
    res = db.session.execute(text("SELECT * FROM sample"))
    assert list(res.keys())[0] == "id"
