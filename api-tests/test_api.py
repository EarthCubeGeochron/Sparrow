import requests
import pytest
from schema import Schema

def get(url, *args, **kwargs):
    uri = "http://backend:5000/api/v1"+url
    return requests.get(uri, *args, **kwargs)

routes = [
    '/session',
    '/analysis',
    '/datum'
]

@pytest.mark.parametrize("path", ["","/"])
def test_api_base_exists(path):
    res = get(path)
    assert res.status_code == 200
    body = res.json()
    assert 'routes' in body

    # Test that routes info dict matches expected structure
    Schema([{
        'route': str,
        'description': str,
        str: object
    }]).validate(body['routes'])

@pytest.mark.parametrize("route", routes)
def test_basic_route_exists(route):
    res = get(route)
    assert res.status_code == 200

def test_api_sustained_load():
    """
    API currently fails on large numbers of requests
    """
    for i in range(200):
        res = get("/sample", params=dict(geometry="%"))
        assert res.status_code == 200
