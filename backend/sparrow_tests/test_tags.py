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
        '''Create a new tag add to db and make sure it was entered'''
        data = json_fixture("tags.json")
        tags = db.model.tags_tag

        new_tag = data["new_tag"]

        db.load_data("tags_tag", new_tag)

        q = db.session.query(tags).filter(tags.name == new_tag["name"]).first()
        assert q.name == new_tag["name"]

    def test_add_tag_to_model(self, client, db):
        """create a new sample and then add a tag to it"""

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
    
    def test_remove_tag_from_model(self, client, db):
        '''Remove a tag from the model created above'''
        data = json_fixture("tags.json")

        new_sample = data['new_sample']
        tag_to_remove = data['new_tag']

        sample = db.model.sample
        tags = db.model.tags_tag

        s = db.session.query(sample).filter(sample.name == new_sample['name']).first()
        t = db.session.query(tags).filter(tags.color == tag_to_remove['color']).first()

        assert len(s.tags_tag_collection) > 0
        assert t.name == tag_to_remove['name']

        tag_id = t.id ## unqiue id assigned in database

        new_tag_collection = []
        for tag in s.tags_tag_collection:
            if tag.id != tag_id:
                new_tag_collection.append(tag)
        
        s.tags_tag_collection = new_tag_collection
        assert len(db.session.dirty) == 1 # we've changed the tag_collection
        try:
            db.session.commit()
        except:
            db.session.rollback()
        
        s = db.session.query(sample).filter(sample.name == new_sample['name']).first()
        exist_col = []
        for tag in s.tags_tag_collection:
            if tag.id == tag_id:
                exist_col.append(tag)
        
        assert len(exist_col) == 0


