from .helpers import json_fixture
import json


class TestTags:
    def test_tag_tables_exist(self, client, db):
        """
        Check if the tags tables were successfully created
        """
        tables = ["tag", "analysis_tag", "datum_tag", "session_tag", "sample_tag", "project_tag"]
        for table in tables:
            assert db.engine.has_table(table, schema="tags")

    def test_default_tags_exist(self, client, db):
        """Checks to make sure the default tags are in the db"""
        res = client.get("/api/v2/tags/tag?all=true")
        d = res.json()
        assert len(d["data"]) >= 3

    def test_post_tag(self, client, db):
        data = json_fixture("tags.json")
        tags = db.model.tags_tag

        new_tag = data["new_tag"]

        db.load_data("tags_tag", new_tag)

        q = db.session.query(tags).filter(tags.name == new_tag["name"]).first()
        assert q.name == new_tag["name"]

    def test_add_tag_to_datum(self, client, db):
        """create a new datum and then add a tag to it"""

        sample = db.model.sample
        tags = db.model.tags_tag

        data = json_fixture("tags.json")
        new_sample = data["new_sample"]

        db.load_data("sample", new_sample)

        q = db.session.query(sample).filter(sample.name == new_sample["name"]).first()

        assert q.name == new_sample["name"]

        sample_id = q.id

        tag = db.session.query(tags).filter(tags.name == data["new_tag"]["name"]).first()

        q.tags_tag_collection.append(tag)
        assert len(db.session.dirty) == 1  # Intermittently Fails here!

        try:
            db.session.commit()
        except:
            db.session.rollback()

        s = db.session.query(sample).get(sample_id)
        assert len(s.tags_tag_collection) != 0