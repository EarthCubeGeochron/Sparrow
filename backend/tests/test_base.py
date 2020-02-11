from sparrow.app import construct_app
from datetime import datetime

app, db = construct_app()

def test_true():
    assert True

session = dict(
    sample_id="A-0",
    date=datetime.now())

def test_imperative_import():
    """
    Test importing some data using imperative SQLAlchemy. This is no longer
    the recommended approach (use import schemas instead). Many records need
    to be inserted to provide a single measurement value, which is tedious.

    However, this imperative method should still work.
    """
    authority = "Carolina Ag. Society"

    sample = db.get_or_create(
        db.model.sample,
        name="A-0")
    db.session.add(sample)

    # Import a single session
    session = db.get_or_create(
        db.model.session,
        sample_id=sample.id,
        date=datetime.now())
    db.session.add(session)

    # Analysis type
    a_type = db.get_or_create(
        db.model.vocabulary_analysis_type,
        id="Insect density inspection",
        authority=authority)
    db.session.add(a_type)

    # Material
    mat = db.get_or_create(
        db.model.vocabulary_material,
        id="long-staple cotton",
        authority=authority)
    db.session.add(mat)

    # Analysis
    analysis = db.get_or_create(
        db.model.analysis,
        session_id=session.id,
        analysis_type=a_type.id,
        material=mat.id)
    db.session.add(analysis)

    # Parameter
    param = db.get_or_create(
        db.model.vocabulary_parameter,
        authority=authority,
        id="weevil density",
        description="Boll weevil density")
    db.session.add(param)

    # Unit
    unit = db.get_or_create(
        db.model.vocabulary_unit,
        id="insects/sq. decimeter",
        description="Insects per square decimeter",
        authority=authority)
    db.session.add(unit)

    # Datum type
    type = db.get_or_create(
        db.model.datum_type,
        parameter=param.id,
        unit=unit.id)
    db.session.add(type)
    db.session.flush()

    # Parameter
    datum = db.get_or_create(
        db.model.datum,
        analysis=analysis.id,
        type=type.id,
        value=121,
        error=22)

    db.session.add(datum)
    db.session.commit()
