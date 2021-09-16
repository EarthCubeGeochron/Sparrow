from click.testing import CliRunner
from sparrow_cli import main_cli

runner = CliRunner()


def test_cli():
    res = runner.invoke(cli, "help")
    assert res.exit_code == 0

    for stream in (res.output, res.stdout):
        assert "--skip-hostname-check" not in stream


def test_compose():
    res = runner.invoke(main_cli, "compose config")
    assert res.exit_code == 0

    # We need to rework using
    # cfg = load(res.output)
    # assert cfg is not None
    # assert 'gateway' in cfg['services']
