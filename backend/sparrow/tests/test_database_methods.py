from sqlalchemy import text


def test_method_exec_query(db):
    res = db.session.execute(text("SELECT * FROM sample"))
    assert list(res.keys())[0] == "id"


def test_infinite_embargo(db):
    """A lab may embargo indefinitely; the date must be readable."""
    res = db.session.execute(
        text("SELECT 'infinity'::timestamp, '-infinity'::timestamp")
    )
    latest, earliest = res.one()
    assert latest.year == 9999
    assert earliest.year == 1
