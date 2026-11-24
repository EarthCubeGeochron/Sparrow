"""Run a pipeline from wherever its files are."""

import json
from importlib import import_module
from os import environ
from pathlib import Path
from typing import Optional

import typer
from rich import print

from .models import top_level_records
from .pipeline import Pipeline, run_pipeline
from .sinks import APISink, DryRunSink

app = typer.Typer(no_args_is_help=True, add_completion=False)


def load_pipeline(spec: str) -> Pipeline:
    """Resolve `package.module:name` to a pipeline instance."""
    module_name, _, attr = spec.partition(":")
    if not attr:
        raise typer.BadParameter("Name a pipeline as 'package.module:name'")
    obj = getattr(import_module(module_name), attr)
    if isinstance(obj, type):
        obj = obj()
    if not isinstance(obj, Pipeline):
        raise typer.BadParameter(f"{spec} is not a sparrow.pipelines.Pipeline")
    return obj


@app.command()
def run(
    pipeline: str = typer.Argument(..., help="The pipeline, as 'package.module:name'"),
    paths: list[Path] = typer.Argument(..., help="Files or directories to read"),
    api: Optional[str] = typer.Option(
        None, help="Base URL of a Sparrow lab to send records to"
    ),
    stop_on_error: bool = False,
):
    """Read files with a pipeline. Without --api this is a dry run: records are
    built and validated, and nothing is sent anywhere."""
    _pipeline = load_pipeline(pipeline)
    if api is None:
        sink = DryRunSink()
    else:
        # A token is a credential, so it is read from the environment
        sink = APISink(api, token=environ.get("SPARROW_API_TOKEN"))

    report = run_pipeline(_pipeline, paths, sink, stop_on_error=stop_on_error)
    for result in report.files:
        if result.status == "failed":
            print(f"[red]{result.source.path}[/red]: {result.error}")
        else:
            print(f"[dim]{result.source.path}[/dim]: {result.n_records} records")
    verb = "validated" if api is None else "sent"
    print(
        f"{report.count('loaded')} files {verb}, [red]{report.count('failed')} failed"
    )
    if not report.ok:
        raise typer.Exit(1)


@app.command()
def schema(model: str = typer.Argument("session")):
    """Print the JSON schema of a record a pipeline can produce."""
    if model not in top_level_records:
        raise typer.BadParameter(f"Choose one of {', '.join(top_level_records)}")
    typer.echo(json.dumps(top_level_records[model].model_json_schema(), indent=2))
