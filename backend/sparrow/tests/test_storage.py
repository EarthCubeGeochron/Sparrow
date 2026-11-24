from macrostrat.utils import relative_path
from moto import mock_aws
from pytest import fixture

from sparrow.core.data_files import download_location
from sparrow.core.storage import ObjectStore, set_object_store

from .test_pipelines import IsotopePipeline


@fixture(scope="class")
def store():
    """A lab's bucket, with one data file in it, and nothing on disk."""
    with mock_aws():
        _store = ObjectStore(
            bucket="lab-data", access_key="test", secret_key="test", prefix="sparrow"
        )
        _store.client.create_bucket(Bucket="lab-data")
        src = relative_path(__file__, "fixtures", "simple-carbon-oxygen-isotopes.csv")
        _store.upload(src, "runs/2020/stored-isotopes.csv")
        _store.upload(src, "runs/2020/notes.txt")
        set_object_store(_store)
        yield _store
        set_object_store(None)


class StoredIsotopes(IsotopePipeline):
    name = "stored-isotopes"

    def read(self, path):
        for sample in super().read(path):
            sample.name = sample.name.replace("Pipeline", "Stored")
            yield sample


def test_addresses():
    store = ObjectStore(bucket="lab-data", prefix="/sparrow/")
    assert store.uri("a/b.csv") == "s3://lab-data/sparrow/a/b.csv"
    assert store.key_for("s3://lab-data/sparrow/a/b.csv") == "a/b.csv"
    assert store.key_for("s3://lab-data/other/a/b.csv") is None
    assert store.key_for("s3://elsewhere/sparrow/a/b.csv") is None


class TestObjectStorePipelines:
    @fixture(scope="class")
    def plugin(self, app, store):
        plugin = app.plugins.get("pipelines")
        saved = plugin._pipelines
        plugin._pipelines = {"stored-isotopes": StoredIsotopes()}
        yield plugin
        plugin._pipelines = saved

    def test_list(self, store):
        keys = [o.key for o in store.list("runs", pattern="*.csv")]
        assert keys == ["runs/2020/stored-isotopes.csv"]
        assert next(store.list("runs", pattern="*.csv")).md5 is not None

    def test_load_from_store(self, db, plugin, store, monkeypatch):
        # Nothing may come from a data directory
        monkeypatch.delenv("SPARROW_DATA_DIR", raising=False)
        report = plugin.run("stored-isotopes")
        assert report.ok
        assert report.count("loaded") == 1

        data_file = (
            db.session.query(db.model.data_file)
            .filter_by(basename="stored-isotopes.csv")
            .one()
        )
        assert data_file.file_path == "runs/2020/stored-isotopes.csv"
        assert (
            data_file.source_url
            == "s3://lab-data/sparrow/runs/2020/stored-isotopes.csv"
        )
        Sample = db.model.sample
        assert (
            db.session.query(Sample).filter(Sample.name.like("Stored sample %")).count()
            > 1
        )

    def test_unchanged_object_is_not_downloaded(self, db, plugin, store, monkeypatch):
        def no_download(key):
            raise AssertionError(f"{key} was downloaded")

        monkeypatch.setattr(store, "downloaded", no_download)
        report = plugin.run("stored-isotopes")
        assert report.count("skipped") == 1
        assert report.count("loaded") == 0

    def test_prefix(self, db, plugin, store):
        report = plugin.run("stored-isotopes", ["runs/1999"])
        assert len(report.files) == 0
        address = "s3://lab-data/sparrow/runs/2020"
        report = plugin.run("stored-isotopes", [address])
        assert report.count("skipped") == 1

    def test_download_location(self, db, store, monkeypatch):
        monkeypatch.delenv("SPARROW_DATA_DIR", raising=False)
        data_file = (
            db.session.query(db.model.data_file)
            .filter_by(basename="stored-isotopes.csv")
            .one()
        )
        location = download_location(data_file)
        assert "lab-data" in location["url"]
        assert "sparrow/runs/2020/stored-isotopes.csv" in location["url"]

    def test_download_from_private_store(self, db, store, client, monkeypatch):
        """A gateway browsers cannot reach: the backend passes the file on."""
        data_file = (
            db.session.query(db.model.data_file)
            .filter_by(basename="stored-isotopes.csv")
            .one()
        )
        monkeypatch.setattr(store, "public", False)
        res = client.get(f"/api/v2/data_file/{data_file.file_hash}/download")
        assert res.status_code == 200
        assert res.text.startswith("height,delta13c")
        assert "stored-isotopes.csv" in res.headers["content-disposition"]

    def test_download_without_store(self, db, store, monkeypatch):
        data_file = (
            db.session.query(db.model.data_file)
            .filter_by(basename="stored-isotopes.csv")
            .one()
        )
        set_object_store(None)
        monkeypatch.delenv("SPARROW_S3_BUCKET", raising=False)
        monkeypatch.delenv("SPARROW_DATA_DIR", raising=False)
        assert download_location(data_file) is None
        monkeypatch.setenv("SPARROW_DATA_DIR", "/data")
        assert download_location(data_file) == {
            "accel_redirect": "/data/runs/2020/stored-isotopes.csv"
        }
        set_object_store(store)
