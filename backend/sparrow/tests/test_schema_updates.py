from pytest import fixture
from geoalchemy2.shape import from_shape
from shapely.geometry import shape
from sparrow.loader import model_interface
import logging

test_sample = {
    "name": "4c1321a",
    "material": "Granite",
    "location": {"coordinates": [-122, 43], "type": "Point"},
}


@fixture
def SampleSchema(db):
    return model_interface(db.model.sample, session=db.session)()


class TestSchemaUpdates:
    def test_load_sample_imperative(self, db):
        """A simple test to make sure we can load a single sample with
        a linked material"""
        Sample = db.model.sample
        Material = db.model.vocabulary_material

        loc = from_shape(shape(test_sample["location"]), srid=4326)

        mat = Material(id="Granitic rock")
        obj = Sample(name="3a24aba", location=loc)
        obj._material = mat
        assert isinstance(obj._material, Material)
        db.session.add(obj)
        db.session.commit()

    def test_load_sample_direct(self, caplog, db, SampleSchema):
        """Test a low-level load and commit of this database object"""

        caplog.set_level(logging.DEBUG, logger="marshmallow")
        res = SampleSchema.load(test_sample, session=db.session)
        assert isinstance(res, db.model.sample)
        assert isinstance(res._material, db.model.vocabulary_material)
        assert id(db.model.vocabulary_material) == id(type(res._material))
        db.session.add(res)
        db.session.commit()

    def test_load_sample_highlevel(self, db):
        """Test a higher-level commit using our load-data infrastructure.
        If this fails while the previous test succeeds, it is likely an
        issue with the way we manage database sessions in the testing
        configuration
        """
        test_sample["name"] = "a8fa3ac"
        db.load_data("sample", test_sample)

    def test_retrieve_sample(self, db):
        obj = db.session.query(db.model.sample).filter_by(name="4c1321a").one()
        assert obj._material.id == "Granite"

    def test_sample_edits_interface(self, db):
        pass
