from click.testing import CliRunner

from sparrow.core.auth.create_user import _create_user
from sparrow.core.auth.orcid import find_users_for_orcid

ORCID = "0000-0002-1825-0097"


def invoke(app, *args):
    # Imported here: building the command group needs the application context
    from sparrow.admin import cli

    return CliRunner().invoke(cli, ["link-orcid", *args], obj=app)


class TestLinkOrcidCommand:
    def test_link(self, app, db):
        _create_user(db, "cli-orcid", "test", raise_on_error=False)
        res = invoke(app, "cli-orcid", f"https://orcid.org/{ORCID}", "--name", "J. C.")
        assert res.exit_code == 0, res.output
        assert "Created researcher J. C." in res.output
        assert find_users_for_orcid(db, ORCID) == ["cli-orcid"]

    def test_relink_is_idempotent(self, app, db):
        res = invoke(app, "cli-orcid", ORCID)
        assert res.exit_code == 0, res.output
        assert "Using researcher J. C." in res.output

    def test_refuses_invalid_id(self, app, db):
        res = invoke(app, "cli-orcid", "0000-0002-1825-0098")
        assert res.exit_code == 1
        assert "check digit" in res.output

    def test_refuses_unknown_user(self, app, db):
        res = invoke(app, "nobody-here", ORCID)
        assert res.exit_code == 1
        assert "No user named nobody-here" in res.output
