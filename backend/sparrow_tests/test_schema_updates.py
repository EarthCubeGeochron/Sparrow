from pytest import mark
from geoalchemy2.shape import from_shape
from shapely.geometry import shape
from sparrow.interface import model_interface
import logging

test_sample = {
    "name": "4c1321a",
    "material": "Granite",
    "location": {"coordinates": [-122, 43], "type": "Point"},
}


class TestSchemaUpdates:
    @mark.skip
    def test_load_sample_imperative(self, db):
        """A simple test to make sure we can load a single sample with
        a linked material"""
        Sample = db.model.sample
        Material = db.model.vocabulary_material

        loc = from_shape(shape(test_sample["location"]))

        mat = Material(id="Granitic rock")
        obj = Sample(name="3a24aba", location=loc)
        obj._material = mat
        assert isinstance(obj._material, Material)
        db.session.add(obj)
        db.session.commit()

    @mark.xfail(reason="We haven't figured this out yet")
    def test_load_sample_direct(self, caplog, db):
        """Test a low-level load and commit of this database object"""
        caplog.set_level(logging.DEBUG, logger="marshmallow")
        SampleSchema = model_interface(db.model.sample, session=db.session)()
        res = SampleSchema.load(test_sample, session=db.session)
        assert isinstance(res, db.model.sample)
        assert (
            SampleSchema.fields["_material"].related_model
            is db.model.vocabulary_material
        )
        assert isinstance(res._material, db.model.vocabulary_material)

        db.session.add(res)
        db.session.commit()

    @mark.xfail(reason="We haven't figured this out yet")
    def test_load_sample_highlevel(self, db):
        """Test a higher-level commit using our load-data infrastructure.
        If this fails while the previous test succeeds, it is likely an
        issue with the way we manage database sessions in the testing
        configuration
        """
        test_sample["name"] = "a8fa3ac"
        db.load_data("sample", test_sample)

    @mark.xfail(reason="We haven't figured this out yet")
    def test_retrieve_sample(self, db):
        obj = db.session.query(db.model.sample).filter_by(name="4c1321a").one()
        assert obj._material.id == "Granite"
