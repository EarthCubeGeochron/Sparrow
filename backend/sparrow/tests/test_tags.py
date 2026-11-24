from .helpers import json_fixture


class TestTags:
    # PostgREST has its own connection, so it sees only committed data
    use_isolation = False

    def test_tag_tables_exist(self, db):
        """
        Check if the tags tables were successfully created
        """
        tables = [
            "tag",
            "analysis_tag",
            "datum_tag",
            "session_tag",
            "sample_tag",
            "project_tag",
        ]
        for table in tables:
            assert db.inspector.has_table(table, schema="tags")

    def test_default_tags_exist(self, db, pg_api):
        """Checks to make sure the default tags are in the db"""
        res = pg_api.get("/tag")
        assert res.status_code == 200
        assert len(res.json()) >= 3

    def test_post_tag_unauthorized(self, pg_api):
        new_tag = json_fixture("tags.json")["new_tag"]
        res = pg_api.post("/tag", json=new_tag)
        assert res.status_code == 401

    def test_post_tag(self, db, pg_api, token):
        """Create a new tag add to db and make sure it was entered"""
        new_tag = json_fixture("tags.json")["new_tag"]
        res = pg_api.post(
            "/tag", headers={"Authorization": "Bearer " + token}, json=new_tag
        )
        assert res.status_code == 201

        tags = db.model.tags_tag
        q = db.session.query(tags).filter(tags.name == new_tag["name"]).first()
        assert q.name == new_tag["name"]

    def test_tag_a_sample(self, db, pg_api, token):
        """Records are tagged by adding a link"""
        auth = {"Authorization": "Bearer " + token}
        sample = db.load_data("sample", json_fixture("tags.json")["new_sample"])
        tag = pg_api.get("/tag", params={"limit": 1}).json()[0]

        res = pg_api.post(
            "/sample_tag",
            headers=auth,
            json={"tag_id": tag["id"], "sample_id": sample.id},
        )
        assert res.status_code == 201

        res = pg_api.get("/sample_tag", params={"sample_id": f"eq.{sample.id}"})
        assert [t["tag_id"] for t in res.json()] == [tag["id"]]

    def test_cleanup(self, db, pg_api, token):
        auth = {"Authorization": "Bearer " + token}
        data = json_fixture("tags.json")
        res = pg_api.delete(
            "/sample", headers=auth, params={"name": f"eq.{data['new_sample']['name']}"}
        )
        assert res.status_code == 204
        res = pg_api.delete(
            "/tag", headers=auth, params={"name": f"eq.{data['new_tag']['name']}"}
        )
        assert res.status_code == 204
