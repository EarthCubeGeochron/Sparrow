from csv import DictReader
from datetime import datetime, timezone
from shutil import copy

from macrostrat.utils import relative_path
from pytest import fixture

from sparrow.core.import_helpers.sink import DatabaseSink
from sparrow.pipelines import (
    Analysis,
    Datum,
    DatumType,
    DryRunSink,
    Pipeline,
    Sample,
    Session,
    run_pipeline,
)


def _datum(row, parameter):
    return Datum(
        value=row[parameter],
        error=row[parameter + "_error"],
        type=DatumType(parameter=parameter, unit="permille"),
    )


class IsotopePipeline(Pipeline):
    """The pipeline of `test_datafile_import`, with no database in sight."""

    name = "stable-isotopes"
    file_type = "Stable isotope table"
    pattern = "*.csv"

    def read(self, path):
        with open(path) as f:
            for row in DictReader(f):
                yield Sample(
                    name=f"Pipeline sample {float(row['height']):.2f}",
                    session=[
                        Session(
                            technique="Stable isotope measurements",
                            date=datetime(1900, 1, 1, tzinfo=timezone.utc),
                            analysis=[
                                Analysis(
                                    analysis_type="Stable isotope measurements",
                                    datum=[
                                        _datum(row, "delta13c"),
                                        _datum(row, "delta18o"),
                                    ],
                                )
                            ],
                        )
                    ],
                )


@fixture(scope="class")
def data_dir(tmp_path_factory):
    root = tmp_path_factory.mktemp("isotopes")
    src = relative_path(__file__, "fixtures", "simple-carbon-oxygen-isotopes.csv")
    copy(src, root / "isotopes.csv")
    (root / "notes.txt").write_text("Not a data file")
    return root


class TestPipelines:
    def test_dry_run_needs_no_database(self, data_dir):
        sink = DryRunSink()
        report = run_pipeline(IsotopePipeline(), [data_dir], sink)
        assert report.ok
        assert report.count("loaded") == 1
        assert len(sink.records) > 1

    def test_load(self, db, data_dir):
        dry = DryRunSink()
        run_pipeline(IsotopePipeline(), [data_dir], dry)
        n_expected = len(dry.records)

        report = run_pipeline(IsotopePipeline(), [data_dir], DatabaseSink(db))
        assert report.ok
        assert report.files[0].n_records == n_expected

        Sample_ = db.model.sample
        n = (
            db.session.query(Sample_)
            .filter(Sample_.name.like("Pipeline sample %"))
            .count()
        )
        assert n == n_expected

        data_file = db.session.query(db.model.data_file).filter_by(
            basename="isotopes.csv"
        )
        assert data_file.count() == 1
        assert data_file.one().type_id == "Stable isotope table"

    def test_unchanged_file_is_skipped(self, db, data_dir):
        report = run_pipeline(IsotopePipeline(), [data_dir], DatabaseSink(db))
        assert report.count("skipped") == 1
        assert report.count("loaded") == 0

    def test_redo(self, db, data_dir):
        n_samples = db.session.query(db.model.sample).count()
        report = run_pipeline(
            IsotopePipeline(), [data_dir], DatabaseSink(db), redo=True
        )
        assert report.count("loaded") == 1
        # Records are matched to existing ones, not duplicated
        assert db.session.query(db.model.sample).count() == n_samples

    def test_changed_file_is_read_again(self, db, data_dir):
        path = data_dir / "isotopes.csv"
        lines = path.read_text().splitlines()
        path.write_text("\n".join(lines[:-1]) + "\n")
        report = run_pipeline(IsotopePipeline(), [data_dir], DatabaseSink(db))
        assert report.count("loaded") == 1
        assert (
            db.session.query(db.model.data_file)
            .filter_by(basename="isotopes.csv")
            .count()
            == 1
        )

    def test_failure_is_recorded(self, db, data_dir):
        bad = data_dir / "bad.csv"
        bad.write_text(
            "height,delta13c,delta13c_error,delta18o,delta18o_error\n1,x,0,0,0\n"
        )
        report = run_pipeline(IsotopePipeline(), [bad], DatabaseSink(db))
        assert report.count("failed") == 1
        Link = db.model.data_file_link
        assert db.session.query(Link).filter(Link.error.isnot(None)).count() == 1


class TestPipelineTasks:
    def test_pipeline_is_registered_as_task(self, app, db, data_dir):
        plugin = app.plugins.get("pipelines")
        plugin._pipelines = {"stable-isotopes": IsotopePipeline()}
        plugin.on_plugins_initialized()

        manager = app.plugins.get("task-manager")
        task = manager.get_task("stable-isotopes")
        task(path=str(data_dir), redo=True)

        names = [t["name"] for t in manager.task_info()]
        assert "stable-isotopes" in names
