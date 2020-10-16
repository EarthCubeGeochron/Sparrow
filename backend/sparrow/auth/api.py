from sparrow.api.response import APIResponse
from sparrow.plugins import SparrowCorePlugin
from starlette.routing import Route, Router


def login(request):
    pass


def logout(request):
    pass


def status(request):
    pass


def refresh(request):
    pass


def secret(request):
    # JWT required
    return APIResponse({"answer": 42})


routes = [
    Route("/login", endpoint=login),
    Route("/logout", endpoint=logout),
    Route("/refresh", endpoint=refresh),
    Route("/status", endpoint=status),
    Route("/secret", endpoint=secret),
]


class AuthV2Plugin(SparrowCorePlugin):
    name = "auth"

    def on_api_initialized_v2(self, api):
        api.mount("/auth", Router(routes))
