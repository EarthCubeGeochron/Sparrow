import asyncio
import time
from urllib.parse import parse_qs, urlparse

import httpx2
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from macrostrat.auth_system.session import AuthSettings
from pytest import fixture, mark, raises
from starlette.testclient import TestClient

from sparrow.broker import BrokerConfigError, BrokerSettings, create_app
from sparrow.core.auth.orcid import BrokerIdentitySource

BROKER = "https://broker.example.org"
LAB = "https://lab.example.edu"
RETURN_TO = f"{LAB}/api/v2/auth/orcid/callback"
ORCID_ID = "0000-0002-1825-0097"
CLIENT_SECRET = "broker-client-secret"


def fake_orcid(request: httpx2.Request) -> httpx2.Response:
    if request.url.path == "/oauth/token":
        body = parse_qs(request.content.decode())
        assert body["redirect_uri"] == [f"{BROKER}/callback"]
        assert body["client_secret"] == [CLIENT_SECRET]
        if body["code"] != ["good"]:
            return httpx2.Response(400, json={"error": "invalid_grant"})
        return httpx2.Response(200, json={"access_token": "orcid-token"})
    assert request.headers["Authorization"] == "Bearer orcid-token"
    return httpx2.Response(
        200, json={"sub": ORCID_ID, "given_name": "Josiah", "family_name": "Carberry"}
    )


def pem(key) -> str:
    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()


@fixture
def key():
    return Ed25519PrivateKey.generate()


@fixture
def settings(key):
    return BrokerSettings(
        url=BROKER + "/",
        orcid_client_id="APP-BROKER",
        orcid_client_secret=CLIENT_SECRET,
        signing_key=key,
    )


def client_for(settings):
    app = create_app(settings, transport=httpx2.MockTransport(fake_orcid))
    return TestClient(app, base_url=BROKER, follow_redirects=False)


@fixture
def client(settings):
    return client_for(settings)


def start(client, return_to=RETURN_TO, state="lab-state"):
    return client.get("/login", params={"return_to": return_to, "state": state})


def sign_in(client, code="good", **kwargs):
    res = start(client, **kwargs)
    assert res.status_code == 307
    state = parse_qs(urlparse(res.headers["location"]).query)["state"][0]
    return client.get("/callback", params={"code": code, "state": state})


def verify(client, assertion, audience=LAB):
    jwks = jwt.PyJWKSet.from_dict(client.get("/.well-known/jwks.json").json())
    kid = jwt.get_unverified_header(assertion)["kid"]
    key = next(k.key for k in jwks.keys if k.key_id == kid)
    return jwt.decode(
        assertion, key, algorithms=["EdDSA"], audience=audience, issuer=BROKER
    )


def test_login_redirects_to_orcid(client):
    res = start(client)
    location = urlparse(res.headers["location"])
    query = parse_qs(location.query)
    assert location.netloc == "orcid.org"
    assert query["redirect_uri"] == [f"{BROKER}/callback"]
    assert query["client_id"] == ["APP-BROKER"]
    assert "broker_state" in res.cookies


def test_sign_in_returns_assertion_to_lab(client):
    res = sign_in(client)
    assert res.status_code == 307
    location = urlparse(res.headers["location"])
    assert f"{location.scheme}://{location.netloc}{location.path}" == RETURN_TO
    query = parse_qs(location.query)
    assert query["state"] == ["lab-state"]
    claims = verify(client, query["assertion"][0])
    assert claims["sub"] == ORCID_ID
    assert claims["name"] == "Josiah Carberry"
    assert claims["state"] == "lab-state"
    assert 0 < claims["exp"] - time.time() <= 120
    assert claims["jti"]
    assert jwt.get_unverified_header(query["assertion"][0])["alg"] == "EdDSA"


def test_assertion_is_only_for_the_returning_lab(client):
    res = sign_in(client)
    assertion = parse_qs(urlparse(res.headers["location"]).query)["assertion"][0]
    with raises(jwt.InvalidAudienceError):
        verify(client, assertion, audience="https://other-lab.example.edu")


def test_local_lab_over_http(client):
    local = "http://sparrow.local:5002/api/v2/auth/orcid/callback"
    res = sign_in(client, return_to=local)
    query = parse_qs(urlparse(res.headers["location"]).query)
    assert verify(client, query["assertion"][0], "http://sparrow.local:5002")


@mark.parametrize(
    "return_to",
    [
        "http://lab.example.edu/api/v2/auth/orcid/callback",
        "https://lab.example.edu/somewhere-else",
        "https://lab.example.edu/api/v2/auth/orcid/callback?next=/x",
        "https://user@lab.example.edu/api/v2/auth/orcid/callback",
        "javascript:alert(1)//api/v2/auth/orcid/callback",
        "/api/v2/auth/orcid/callback",
    ],
)
def test_unsafe_return_to_is_refused(client, return_to):
    assert start(client, return_to=return_to).status_code == 400


def test_allowlist(key):
    settings = BrokerSettings(
        url=BROKER,
        orcid_client_id="APP-BROKER",
        orcid_client_secret=CLIENT_SECRET,
        signing_key=key,
        allowed_origins=["https://LAB.example.edu/"],
    )
    client = client_for(settings)
    assert start(client).status_code == 307
    other = "https://other.example.edu/api/v2/auth/orcid/callback"
    assert start(client, return_to=other).status_code == 400


def test_state_must_match_cookie(client):
    res = start(client)
    state = parse_qs(urlparse(res.headers["location"]).query)["state"][0]
    client.cookies.clear()
    assert (
        client.get("/callback", params={"code": "good", "state": state}).status_code
        == 400
    )


def test_forged_state_is_refused(client, settings):
    start(client)
    forged = jwt.encode(
        {"type": "broker-state", "nonce": "x", "return_to": RETURN_TO},
        "not-the-key",
        algorithm="HS256",
    )
    res = client.get("/callback", params={"code": "good", "state": forged})
    assert res.status_code == 400


def test_bad_code_is_refused(client):
    assert sign_in(client, code="bad").status_code == 400


def test_cancelled_sign_in_returns_to_lab(client):
    res = start(client)
    state = parse_qs(urlparse(res.headers["location"]).query)["state"][0]
    res = client.get("/callback", params={"error": "access_denied", "state": state})
    assert res.status_code == 307
    query = parse_qs(urlparse(res.headers["location"]).query)
    assert query == {"error": ["access_denied"], "state": ["lab-state"]}


def test_jwks_holds_only_the_public_key(client, key):
    data = client.get("/.well-known/jwks.json").json()
    [jwk] = data["keys"]
    assert jwk["kty"] == "OKP" and jwk["alg"] == "EdDSA"
    assert "d" not in jwk


class TestSettings:
    def env(self, key, **extra):
        env = {
            "SPARROW_BROKER_URL": BROKER,
            "SPARROW_BROKER_ORCID_CLIENT_ID": "APP-BROKER",
            "SPARROW_BROKER_ORCID_CLIENT_SECRET": CLIENT_SECRET,
            "SPARROW_BROKER_SIGNING_KEY": pem(key),
        }
        env.update(extra)
        return env

    def test_from_env(self, key):
        env = self.env(
            key, SPARROW_BROKER_ALLOWED_ORIGINS="https://a.org, https://b.org"
        )
        settings = BrokerSettings.from_env(env)
        assert settings.allowed_origins == ["https://a.org", "https://b.org"]
        assert CLIENT_SECRET not in repr(settings)

    def test_key_from_file(self, key, tmp_path):
        path = tmp_path / "key.pem"
        path.write_text(pem(key))
        env = self.env(key, SPARROW_BROKER_SIGNING_KEY_FILE=str(path))
        del env["SPARROW_BROKER_SIGNING_KEY"]
        assert BrokerSettings.from_env(env).kid

    def test_refuses_other_key_types(self, key):
        rsa = pem(generate_private_key(public_exponent=65537, key_size=2048))
        with raises(BrokerConfigError) as err:
            BrokerSettings.from_env(self.env(key, SPARROW_BROKER_SIGNING_KEY=rsa))
        assert "PRIVATE KEY" not in str(err.value)

    def test_requires_configuration(self, key):
        env = self.env(key)
        del env["SPARROW_BROKER_ORCID_CLIENT_SECRET"]
        with raises(BrokerConfigError):
            BrokerSettings.from_env(env)


def test_lab_accepts_the_brokers_assertion(settings):
    """The lab's verifier, reading keys from this broker, accepts what it signs."""
    broker_app = create_app(settings, transport=httpx2.MockTransport(fake_orcid))
    client = TestClient(broker_app, base_url=BROKER, follow_redirects=False)
    res = sign_in(client, state="lab-state")
    query = parse_qs(urlparse(res.headers["location"]).query)

    lab = AuthSettings(
        secret_key="lab-secret",
        oauth_client_id="",
        oauth_client_secret="",
        redirect_uri=RETURN_TO,
    )
    source = BrokerIdentitySource(
        BROKER, lab, transport=httpx2.ASGITransport(app=broker_app)
    )
    params = {"assertion": query["assertion"][0]}
    identity = run(source.identify(params, "lab-state"))
    assert identity.sub == ORCID_ID
    assert identity.name == "Josiah Carberry"


def run(coroutine):
    # Unlike asyncio.run, leaves the thread's event loop alone for later tests
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coroutine)
    finally:
        loop.close()
