from click.testing import CliRunner
from main import cli
from yaml import load, Loader

runner = CliRunner()


def test_cli():
    res = runner.invoke(cli, "help")
    assert res.exit_code == 0

    for stream in (res.output, res.stdout):
        assert "--skip-hostname-check" not in stream


def test_compose():
    res = runner.invoke(cli, "compose config")
    assert res.exit_code == 0

    cfg = load(res.output)
    assert cfg is not None
    assert 'gateway' in cfg['services']
