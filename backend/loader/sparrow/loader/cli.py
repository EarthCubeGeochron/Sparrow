import typer
import warnings
from rich import print
from typing import List
from marshmallow import ValidationError
from . import show_loader_schemas, validate_data
import json
import sys

app = typer.Typer(no_args_is_help=True)


@app.command(
    name="show-schemas",
    help="Show loader schemas for Sparrow database models",
)
def show_schemas(nest_depth: int = 0, show_dump_only=False):
    """Print the loader schema for a Sparrow database model"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        show_loader_schemas(nest_depth=nest_depth, show_dump_only=show_dump_only)


@app.command(name="show-schema")
def show_schema(schema: str, nest_depth: int = 0, show_dump_only=False):
    """Show a single loader schema for a Sparrow database model"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        show_loader_schemas(
            schema, nest_depth=nest_depth, show_dump_only=show_dump_only
        )


@app.command(
    name="validate",
    help="Validate data piped from stdin",
)
def _validate_data(model_name: str):
    """Check a dictionary of data against a Sparrow database model"""
    data = json.load(sys.stdin)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            res = validate_data(model_name, data)
            print("[bold green]Success![/bold green]")
            print(res)
        except ValidationError as e:
            print("[bold red]Validation error![/bold red]")
            print(e)
