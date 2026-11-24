"""What the retired API routes served, now read through PostgREST."""

from pytest import mark


class TestPostgRESTAPI:
    use_isolation = False

    def test_load_searchable_sample(self, db):
        db.load_data("sample", {"name": "Obsidian flow 7", "material": "obsidian"})

    @mark.parametrize(
        "route",
        [
            "researcher",
            "publication",
            "instrument",
            "datum_type",
            "material",
            "method",
            "parameter",
            "unit",
            "error_metric",
            "analysis_type",
            "authority",
            "age_context",
            "tag",
        ],
    )
    def test_supporting_records(self, pg_api, route):
        res = pg_api.get("/" + route, params={"limit": 2})
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_vocabulary_has_loaded_term(self, pg_api):
        res = pg_api.get("/material", params={"id": "eq.obsidian"})
        assert len(res.json()) == 1

    def test_metrics(self, pg_api):
        res = pg_api.get("/metrics")
        assert res.status_code == 200
        (metrics,) = res.json()
        assert metrics["number_of_samples"] >= 1

    def test_search(self, pg_api):
        res = pg_api.get("/rpc/search", params={"term": "obsidian"})
        assert res.status_code == 200
        found = res.json()
        samples = [r["data"]["name"] for r in found if r["model"] == "sample"]
        assert "Obsidian flow 7" in samples

    def test_search_no_match(self, pg_api):
        res = pg_api.get("/rpc/search", params={"term": "zzzzunmatched"})
        assert res.json() == []

    def test_data_files_are_not_public(self, pg_api, token):
        res = pg_api.get("/data_file")
        assert res.status_code == 401
        res = pg_api.get("/data_file", headers={"Authorization": "Bearer " + token})
        assert res.status_code == 200

    def test_cleanup(self, pg_api, token):
        res = pg_api.delete(
            "/sample",
            params={"name": "eq.Obsidian flow 7"},
            headers={"Authorization": "Bearer " + token},
        )
        assert res.status_code == 204
