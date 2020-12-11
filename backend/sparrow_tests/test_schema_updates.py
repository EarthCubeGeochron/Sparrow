from pytest import mark
from geoalchemy2.shape import from_shape
from shapely.geometry import shape

test_sample = {
    "name": "4c1321a",
    "material": "Granite",
    "location": {"coordinates": [-122, 43], "type": "Point"}
}


class TestSchemaUpdates:
    def test_load_sample_imperative(self, db):
        """A simple test to make sure we can load a single sample with
        a linked material"""
        Sample = db.model.sample
        Material = db.model.vocabulary_material

        loc = from_shape(shape(test_sample["location"]))

        mat = Material(id="Granitic rock")
        obj = Sample(name="3a24aba", location=loc)
        obj._material = mat
        db.session.add(obj)
        db.session.commit()

    def test_load_sample_direct(self, db):
        """Test a low-level load and commit of this database object"""
        SampleSchema = db.interface.sample()
        assert SampleSchema.opts.model is db.model.sample
        res = SampleSchema.load(test_sample, session=db.session)
        db.session.add(res)
        db.session.commit()

    def test_load_sample_highlevel(self, db):
        """Test a higher-level commit using our load-data infrastructure.
        If this fails while the previous test succeeds, it is likely an
        issue with the way we manage database sessions in the testing
        configuration
        """
        test_sample['name'] = "a8fa3ac"
        db.load_data("sample", test_sample)

    def test_retrieve_sample(self, db):
        obj = db.session.query(db.model.sample).filter_by(name="4c1321a").one()
        assert obj.material.id == "Granite"
