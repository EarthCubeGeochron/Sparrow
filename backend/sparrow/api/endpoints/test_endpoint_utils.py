from .utils import construct_schema_fields_object


class TestEndpointUtils:
    def test_schema_fields_constructor(self, db):
        worked = 0
        for Schema in db.interface:
            schema = Schema(many=True)
            try:
                construct_schema_fields_object(schema)
                worked += 1
            except:
                continue
        assert worked == len(db.interface)

    def test_schema_fields_description(self, db):
        sample = db.interface.sample(many=True)
        