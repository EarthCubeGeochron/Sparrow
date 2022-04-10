from .base import Project_edits_api
from sparrow.core.plugins import SparrowCorePlugin


class ProjectEdits(SparrowCorePlugin):
    name = "project-edits"

    def on_api_initialized_v2(self, api):
        api.mount("/project", Project_edits_api, name="project-edits")
