from yaml import load
from os import environ
from sparrow.interface import load_data
from click import command, echo, secho
from pathlib import Path

def data_directory():
    varname = "SPARROW_DATA_DIR"
    env = environ.get(varname, None)
    if env is None:
        v = style(varname, fg='cyan', bold=True)
        echo(f"Environment variable {v} is not set.")
        secho("Aborting", fg='red', bold=True)
        return
    path = Path(env)
    assert path.is_dir()
    return path


@command()
def cli(stop_on_error=False, verbose=False):
    """
    Import test data
    """

    path = data_directory()

    files = path.glob("**/*.yaml")
    for fn in files:
        print(fn)
        with open(fn) as f:
            data = load(f)
        load_data(data)

if __name__ == '__main__':
    cli()
