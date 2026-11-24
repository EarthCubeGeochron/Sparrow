from datetime import datetime

from pydantic import ValidationError
from pytest import raises

from sparrow.pipelines import (
    Analysis,
    Datum,
    DatumType,
    DryRunSink,
    Pipeline,
    Point,
    Sample,
    Session,
    run_pipeline,
)


def _session(value=1.0):
    return Session(
        date=datetime(2020, 1, 1),
        sample=Sample(name="A", location=Point(coordinates=(-110, 32))),
        analysis=[
            Analysis(
                analysis_type="Test",
                datum=[Datum(value=value, type=DatumType(parameter="age", unit="Ma"))],
            )
        ],
    )


def test_import_data_is_minimal():
    data = _session().to_import_data()
    assert data["sample"] == {
        "name": "A",
        "location": {"type": "Point", "coordinates": [-110.0, 32.0]},
    }
    analysis = data["analysis"][0]
    assert "attribute" not in analysis
    assert analysis["datum"][0]["type"] == {"parameter": "age", "unit": "Ma"}


def test_rejects_nan_and_unknown_fields():
    with raises(ValidationError):
        _session(value=float("nan"))
    with raises(ValidationError):
        Sample(name="A", colour="red")


class LinePipeline(Pipeline):
    name = "lines"
    pattern = "*.txt"

    def read(self, path):
        for line in path.read_text().splitlines():
            yield _session(float(line))


def test_dry_run(tmp_path):
    (tmp_path / "good.txt").write_text("1\n2\n")
    (tmp_path / "bad.txt").write_text("1\nnot a number\n")
    (tmp_path / "ignored.csv").write_text("")

    sink = DryRunSink()
    report = run_pipeline(LinePipeline(), [tmp_path], sink)
    assert report.count("loaded") == 1
    assert report.count("failed") == 1
    assert not report.ok
    # A file is loaded whole or not at all
    assert len(sink.records) == 2


class NamedByFolder(Pipeline):
    name = "by-folder"

    def read_source(self, source, path):
        yield Session(
            date=datetime(2020, 1, 1), sample=Sample(name=source.path.parent.name)
        )


def test_source_name_is_available(tmp_path):
    (tmp_path / "Project A").mkdir()
    (tmp_path / "Project A" / "run.txt").write_text("1")
    sink = DryRunSink()
    run_pipeline(NamedByFolder(), [tmp_path], sink)
    assert sink.records[0].sample.name == "Project A"
