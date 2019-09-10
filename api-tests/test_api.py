import requests
import pytest

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


def test_datum_exists():
    res = get("/datum")
    assert res.status_code == 200
