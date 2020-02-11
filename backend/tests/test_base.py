from sparrow.app import construct_app
from datetime import datetime

app, db = construct_app()


session = dict(
    sample_id="A-0",
    date=datetime.now())


class TestImperativeImport:
    def test_imperative_import(self):
        """
        Test importing some data using imperative SQLAlchemy. This is no
        longer the recommended approach (use import schemas instead). Many
        records must be inserted to successfully provide a single
        measured value, as can be seen below.

        Because this import method relies on fairly low-level SQLAlchemy
        code, it should work for more unusual import tasks that cannot be
        handled by the newer schema-based functionality.
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
        # not sure why we need to flush here...
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

    def test_import_successful(self):
        item = db.session.query(db.model.datum).first()
        assert item.value == 121
        assert item.error == 22

    def test_operation_log(self):
        """
        Test whether our PGMemento audit trail is working
        """
        res = db.session.execute("SELECT count(*) "
                                 "FROM pgmemento.table_event_log")
        total_ops = res.scalar()
        assert total_ops > 0

        res = db.session.execute("SELECT table_operation, table_name "
                                 "FROM pgmemento.table_event_log "
                                 "ORDER BY id DESC LIMIT 1")
        (op, tbl) = res.first()
        assert op == "INSERT"
        assert tbl == "datum"
