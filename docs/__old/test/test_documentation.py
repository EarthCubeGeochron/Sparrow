import requests
import pytest


def get(url, *args, **kwargs):
    uri = "http://sparrow_docs" + url
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

    # We need to keep this exception until we solve redirects
    if route == "/docs":
        assert res.status_code != 200
        return

    assert res.status_code == 200
