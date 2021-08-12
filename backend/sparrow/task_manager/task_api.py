from sparrow.api import APIResponse
from sparrow.context import get_plugin
from starlette.routing import Route, Router
from starlette.authentication import requires


@requires("admin")
async def tasks(request):
    mgr = get_plugin("task-manager")
    return APIResponse(
        [{"name": k, "description": v.__doc__.strip()} for k, v in mgr._tasks.items()]
    )


TasksAPI = Router([Route("/", endpoint=tasks, methods=["GET"])])
