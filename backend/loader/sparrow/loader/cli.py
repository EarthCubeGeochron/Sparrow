import typer
import warnings
from rich import print
from typing import List
from marshmallow import ValidationError
from . import show_loader_schemas, validate_data
import json
import sys

app = typer.Typer()


@app.command(
    name="show-schemas",
    help="Show loader schemas for Sparrow database models",
)
def show_schemas(schemas: List[str] = [], nest_depth: int = 0):
    """Print the loader schema for a Sparrow database model"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        show_loader_schemas(*schemas, nest_depth=nest_depth)


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
