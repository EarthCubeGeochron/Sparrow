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

    def test_post_tag(self, client, db, token):
        '''Create a new tag add to db and make sure it was entered'''
        data = json_fixture("tags.json")
        tags = db.model.tags_tag

        new_tag = data["new_tag"]

        res = client.post("/api/v2/tags/tag", headers = {"Authorization": token},json=new_tag)

        assert res.status_code == 200

        q = db.session.query(tags).filter(tags.name == new_tag["name"]).first()
        assert q.name == new_tag["name"]
    
    def test_edit_tag(self, client, db, token):
        '''Edit a tag's name and color'''
        data = json_fixture("tags.json")

        new_tag = data['new_tag']
        tags = db.model.tags_tag 

        t = db.session.query(tags).filter(tags.name == new_tag['name']).first()
        edits = data['edit_tag']

        res = client.put(f"/api/v2/tags/tag/{t.id}", headers={"Authorization":token},json=data['edit_tag'])

        t = db.session.query(tags).filter(tags.name == edits['name']).first()

        assert t.description == edits['description']

    def test_tag_plugin_endpoints(self, client, db, token):
        data = json_fixture("tags.json")

        sample = data['new_sample']

        sample_ = db.load_data('sample', sample)

        sample_id = sample_.id

        tag = db.session.query(db.model.tags_tag).first()
        tag_id = tag.id

        body = {}
        body['tag_ids'] = [tag_id]
        body['model_id'] = sample_id

        res = client.put('/api/v2/tags/models/sample', headers={"Authorization":token}, json=body)
        
        assert res.status_code == 200


