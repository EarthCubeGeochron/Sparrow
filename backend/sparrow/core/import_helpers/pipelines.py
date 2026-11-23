"""Running pipelines on the server: from its command line, or as a task."""

from pathlib import Path
from typing import Optional

import click

from sparrow.core.context import get_database, get_plugin
from sparrow.core.plugins import SparrowCorePlugin
from sparrow.core.task_manager.base import task
from sparrow.logs import get_logger
from sparrow.pipelines import DryRunSink, Pipeline, RunReport, run_pipeline

from .sink import DatabaseSink
from .util import get_data_directory

log = get_logger(__name__)


class PipelinesPlugin(SparrowCorePlugin):
    """Collects the pipelines a lab has defined. A plugin adds one with

    def on_define_pipelines(self, pipelines):
        pipelines.append(MyPipeline())
    """

    name = "pipelines"

    def __init__(self, app):
        super().__init__(app)
        self._pipelines: Optional[dict[str, Pipeline]] = None

    @property
    def pipelines(self) -> dict[str, Pipeline]:
        if self._pipelines is None:
            found: list[Pipeline] = []
            self.app.run_hook("define-pipelines", found)
            self._pipelines = {p.name: p for p in found}
        return self._pipelines

    def get(self, name: str) -> Pipeline:
        try:
            return self.pipelines[name]
        except KeyError:
            known = ", ".join(self.pipelines) or "none are defined"
            raise click.BadParameter(f"No pipeline named '{name}' ({known})")

    def run(self, name, paths=None, *, redo=False, dry_run=False) -> RunReport:
        pipeline = self.get(name)
        if not paths:
            data_dir = get_data_directory()
            if data_dir is None:
                raise click.UsageError("Give paths to read, or set SPARROW_DATA_DIR")
            paths = [data_dir]
        sink = DryRunSink() if dry_run else DatabaseSink(get_database())
        return run_pipeline(pipeline, [Path(p) for p in paths], sink, redo=redo)

    def on_setup_cli(self, cli):
        cli.add_command(_run_pipeline)


def _summarize(report: RunReport) -> str:
    return ", ".join(
        f"{report.count(status)} files {status}"
        for status in ("loaded", "skipped", "failed")
    )


@click.command(name="run-pipeline")
@click.argument("name")
@click.argument("paths", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option("--redo", is_flag=True, help="Read files that are already loaded")
@click.option("--dry-run", is_flag=True, help="Build records without loading them")
def _run_pipeline(name, paths, redo=False, dry_run=False):
    """Load data files with a pipeline (by default, from the data directory)"""
    report = get_plugin("pipelines").run(name, paths, redo=redo, dry_run=dry_run)
    for result in report.files:
        if result.status == "failed":
            click.secho(f"{result.source.path}: {result.error}", fg="red")
    click.echo(_summarize(report))
    if not report.ok:
        raise click.exceptions.Exit(1)


@task(name="run-pipeline")
def run_pipeline_task(name: str, path: str = "", redo: bool = False):
    """Load data files with a pipeline."""
    paths = [path] if path else None
    report = get_plugin("pipelines").run(name, paths, redo=redo)
    print(_summarize(report))
