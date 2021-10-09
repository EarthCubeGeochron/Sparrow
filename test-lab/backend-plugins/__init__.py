import sparrow
from sparrow.plugins import SparrowPlugin
from sparrow.database import User, on_conflict
from json import load
from os import path

_test_data = path.abspath(path.join(path.dirname(__file__), "project-dump.json"))


class TestDataInitPlugin(SparrowPlugin):
    """A plugin to initialize a test dataset on each app startup"""

    name = "test-init"

    def on_database_ready(self, db):
        """Create a user directly in the database"""
        # Create a user directly in the database
        with on_conflict("do-nothing"):
            user = User(username="Test")
            user.set_password("Test")
            db.session.add(user)
            db.session.commit()

    def on_database_ready(self):
        """Loads testing data on app startup."""
        ## TODO: running importers on app lifecycle methods is a bad idea,
        # because we might run the method on several workers in production.
        db = self.app.database
        project_count = db.session.query(db.model.project).count()
        if project_count > 0:
            return
        db = self.app.database
        data = load(open(_test_data, "r"))
        db.load_data("project", data["data"])


@sparrow.task()
def log_sessions():
    db = sparrow.get_database()
    sessions = db.session.query(db.model.session).all()
    for session in sessions:
        print(session.uuid)
