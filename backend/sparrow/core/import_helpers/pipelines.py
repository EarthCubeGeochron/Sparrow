"""Running pipelines on the server: from its command line, or as a task."""

from pathlib import Path
from typing import Optional

import click

from sparrow.core.context import get_database, get_plugin
from sparrow.core.plugins import SparrowCorePlugin
from sparrow.core.storage import get_object_store
from sparrow.core.task_manager.base import SparrowTask
from sparrow.logs import get_logger
from sparrow.pipelines import DryRunSink, Pipeline, RunReport, run_pipeline, run_sources

from .object_sources import stored_sources
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
        """Run a pipeline over the lab's files: objects in its store where it
        has one (paths are then key prefixes), and otherwise its data directory."""
        pipeline = self.get(name)
        sink = DryRunSink() if dry_run else DatabaseSink(get_database())
        store = get_object_store()
        if store is not None:
            prefixes = [str(p) for p in paths] if paths else [""]
            sources = stored_sources(pipeline, store, prefixes)
            return run_sources(pipeline, sources, sink, redo=redo)
        if not paths:
            data_dir = get_data_directory()
            if data_dir is None:
                raise click.UsageError(
                    "Give paths to read, or set SPARROW_S3_BUCKET or SPARROW_DATA_DIR"
                )
            paths = [data_dir]
        return run_pipeline(pipeline, [Path(p) for p in paths], sink, redo=redo)

    def on_plugins_initialized(self):
        """Each pipeline is a task under its own name, so `sparrow run <name>`
        loads it in the backend or on the task worker."""
        manager = self.app.plugins.get("task-manager")
        for name in self.pipelines:
            manager.register_task(
                _pipeline_task(self, name), name=name, base=SparrowTask
            )

    def on_setup_cli(self, cli):
        cli.add_command(_run_pipeline)


def _pipeline_task(plugin, name):
    def run(path: str = "", redo: bool = False):
        report = plugin.run(name, [path] if path else None, redo=redo)
        print(_summarize(report))

    run.__name__ = name.replace("-", "_")
    run.__doc__ = f"Load data files with the {name} pipeline."
    return run


def _summarize(report: RunReport) -> str:
    return ", ".join(
        f"{report.count(status)} files {status}"
        for status in ("loaded", "skipped", "failed")
    )


@click.command(name="run-pipeline")
@click.argument("name")
@click.argument("paths", nargs=-1)
@click.option("--redo", is_flag=True, help="Read files that are already loaded")
@click.option("--dry-run", is_flag=True, help="Build records without loading them")
def _run_pipeline(name, paths, redo=False, dry_run=False):
    """Load data files with a pipeline. Paths are key prefixes in the lab's
    object store, or files and directories where it has none; by default,
    everything is read."""
    report = get_plugin("pipelines").run(name, paths, redo=redo, dry_run=dry_run)
    for result in report.files:
        if result.status == "failed":
            click.secho(f"{result.source.path}: {result.error}", fg="red")
    click.echo(_summarize(report))
    if not report.ok:
        raise click.exceptions.Exit(1)
