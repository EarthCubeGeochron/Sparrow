from pytest import mark

test_sample = {
    "name": "4c1321a",
    "material": "Granite",
    "location": {"coordinates": [-122, 43], "type": "Point"}
}


class TestSchemaUpdates:
    def test_load_sample_direct(self, db):
        """Test a low-level load and commit of this database object"""
        SampleSchema = db.interface.sample()
        res = SampleSchema.load(test_sample, session=db.session)
        db.session.add(res)
        db.session.commit()

    def test_load_sample_highlevel(self, db):
        """Test a higher-level commit using our load-data infrastructure.
        If this fails while the previous test succeeds, it is likely an
        issue with the way we manage database sessions in the testing
        configuration
        """
        test_sample.name = "a8fa3ac"
        db.load_data("sample", test_sample)

    def test_retrieve_sample(self, db):
        obj = db.session.query(db.model.sample).filter_by(name="4c1321a").one()
        assert obj.material.id == "Granite"
