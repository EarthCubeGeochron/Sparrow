import requests
import pytest


def get(url, *args, **kwargs):
    uri = "http://frontend:8000" + url
    return requests.get(uri, *args, **kwargs)


routes = [
    "/",
    "/docs",
    "/docs/motivation-and-design",
    "/docs/getting-started",
    "/docs/schema",
]


@pytest.mark.parametrize("route", routes)
def test_route_exists(route):
    res = get(route)
    assert res.status_code == 200
