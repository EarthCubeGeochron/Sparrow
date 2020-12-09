from pytest import mark


class TestSchemaUpdates:
    # @mark.xfail(reason="I have no idea why this fails")
    def test_load_data(self, db):
        test_sample = {
            "name": "4c1321a",
            # "material": "Granite",
            "location": {"coordinates": [-122, 43], "type": "Point"}
        }

        db.load_data("sample", test_sample)

    def test_retrieve_sample(self, db):
        obj = db.session.query(db.model.sample).filter_by(name="4c1321a").one()
        assert obj.material.id == "Granite"

    def test_update_data(self):
        pass
