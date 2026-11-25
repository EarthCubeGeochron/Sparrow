import asyncio
import time
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

import httpx2
import jwt
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from jwt.algorithms import OKPAlgorithm
from pytest import fixture, mark, raises
from starlette.testclient import TestClient

from sparrow.core.auth.create_user import _create_user
from sparrow.core.auth.orcid import (
    CALLBACK_PATH,
    AccountLinkError,
    find_users_for_orcid,
    link_orcid,
    normalize_orcid,
    orcid_sign_in_from_env,
)

SECRET_KEY = "test_secret_must_be_at_least_32_characters"
LAB = "http://testserver"
REDIRECT_URI = LAB + CALLBACK_PATH
BROKER = "https://broker.example.org"
LINKED = "0000-0002-1825-0097"
UNLINKED = "0000-0002-1694-233X"
USERNAME = "orcid-user"
CLIENT_SECRET = "client-secret-value"

broker_key = Ed25519PrivateKey.generate()


def fake_orcid(request: httpx2.Request) -> httpx2.Response:
    """ORCID's token and userinfo endpoints; the code names whose iD is returned."""
    if request.url.path == "/oauth/token":
        body = parse_qs(request.content.decode())
        assert body["client_secret"] == [CLIENT_SECRET]
        assert body["redirect_uri"] == [REDIRECT_URI]
        ids = {"linked": LINKED, "unlinked": UNLINKED}
        code = body["code"][0]
        if code not in ids:
            return httpx2.Response(400, json={"error": "invalid_grant"})
        return httpx2.Response(200, json={"access_token": f"token-{code}"})
    token = request.headers["Authorization"].removeprefix("Bearer token-")
    sub = {"linked": LINKED, "unlinked": UNLINKED}[token]
    return httpx2.Response(
        200, json={"sub": sub, "given_name": "Josiah", "family_name": "Carberry"}
    )


def fake_broker(request: httpx2.Request) -> httpx2.Response:
    assert str(request.url) == f"{BROKER}/.well-known/jwks.json"
    return httpx2.Response(200, json={"keys": [public_jwk(broker_key, "key-1")]})


def public_jwk(key, kid):
    jwk = OKPAlgorithm.to_jwk(key.public_key(), as_dict=True)
    return {**jwk, "kid": kid, "alg": "EdDSA", "use": "sig"}


def assertion(lab_state, key=broker_key, kid="key-1", algorithm="EdDSA", **claims):
    now = int(time.time())
    payload = {
        "iss": BROKER,
        "aud": LAB,
        "sub": LINKED,
        "name": "Josiah Carberry",
        "iat": now,
        "exp": now + 120,
        "jti": uuid4().hex,
        "state": lab_state,
    }
    payload.update(claims)
    return jwt.encode(payload, key, algorithm=algorithm, headers={"kid": kid})


def direct_env(**extra):
    env = {
        "SPARROW_SECRET_KEY": SECRET_KEY,
        "SPARROW_ORCID_CLIENT_ID": "APP-TEST",
        "SPARROW_ORCID_CLIENT_SECRET": CLIENT_SECRET,
        "SPARROW_ORCID_REDIRECT_URI": REDIRECT_URI,
    }
    env.update(extra)
    return env


def broker_env(**extra):
    env = {
        "SPARROW_SECRET_KEY": SECRET_KEY,
        "SPARROW_ORCID_BROKER_URL": BROKER,
        "SPARROW_ORCID_REDIRECT_URI": REDIRECT_URI,
    }
    env.update(extra)
    return env


@fixture
def use_orcid(app):
    """Install an ORCID configuration on the running app for one test."""
    plugin = app.plugins.get("auth")
    previous = plugin.orcid

    def _use(orcid):
        plugin.orcid = orcid
        return orcid

    yield _use
    plugin.orcid = previous


@fixture
def browser(app):
    return TestClient(app, follow_redirects=False)


@fixture(scope="class")
def linked_user(db):
    _create_user(db, USERNAME, "test", raise_on_error=False)
    link_orcid(db, USERNAME, LINKED)
    return USERNAME


def start_sign_in(browser, return_url="/projects"):
    res = browser.get("/api/v2/auth/orcid/login", params={"return_url": return_url})
    assert res.status_code == 307
    location = urlparse(res.headers["location"])
    return location, parse_qs(location.query)


def sign_in_directly(browser, code):
    _, query = start_sign_in(browser)
    state = query["state"][0]
    return browser.get(
        "/api/v2/auth/orcid/callback", params={"code": code, "state": state}
    )


def sign_in_with_broker(browser, make_assertion=None):
    _, query = start_sign_in(browser)
    state = query["state"][0]
    token = assertion(state) if make_assertion is None else make_assertion(state)
    return browser.get(
        "/api/v2/auth/orcid/callback", params={"assertion": token, "state": state}
    )


def is_session(browser):
    status = browser.get("/api/v2/auth/status").json()
    secret = browser.get("/api/v2/auth/secret")
    return (
        status["login"] and status["username"] == USERNAME and secret.status_code == 200
    )


class TestOrcidConfiguration:
    def test_off_without_configuration(self):
        assert orcid_sign_in_from_env({"SPARROW_SECRET_KEY": SECRET_KEY}) is None

    def test_direct(self):
        orcid = orcid_sign_in_from_env(direct_env())
        assert orcid.mode == "direct"
        assert orcid.settings.redirect_uri == REDIRECT_URI

    def test_broker(self):
        assert orcid_sign_in_from_env(broker_env()).mode == "broker"

    def test_direct_wins_over_broker(self):
        env = direct_env(SPARROW_ORCID_BROKER_URL=BROKER)
        assert orcid_sign_in_from_env(env).mode == "direct"

    def test_direct_needs_a_secret(self):
        env = broker_env(SPARROW_ORCID_CLIENT_ID="APP-TEST")
        assert orcid_sign_in_from_env(env).mode == "broker"
        env = direct_env()
        del env["SPARROW_ORCID_CLIENT_SECRET"]
        assert orcid_sign_in_from_env(env) is None

    def test_callback_from_domain(self):
        env = direct_env(SPARROW_DOMAIN="lab.example.edu")
        del env["SPARROW_ORCID_REDIRECT_URI"]
        uri = orcid_sign_in_from_env(env).settings.redirect_uri
        assert uri == "https://lab.example.edu" + CALLBACK_PATH
        env["SPARROW_HTTPS_PORT"] = "8443"
        uri = orcid_sign_in_from_env(env).settings.redirect_uri
        assert uri == "https://lab.example.edu:8443" + CALLBACK_PATH

    def test_off_without_public_address(self):
        env = direct_env()
        del env["SPARROW_ORCID_REDIRECT_URI"]
        assert orcid_sign_in_from_env(env) is None

    def test_sandbox(self):
        env = direct_env(SPARROW_ORCID_BASE_URL="https://sandbox.orcid.org/oauth/")
        settings = orcid_sign_in_from_env(env).settings
        assert settings.oauth_token_url == "https://sandbox.orcid.org/oauth/token"


class TestOrcidAccounts:
    @mark.parametrize(
        "value",
        [
            "0000-0002-1694-233X",
            "0000-0002-1694-233x",
            "https://orcid.org/0000-0002-1694-233X",
            "http://orcid.org/0000-0002-1694-233X/",
            " orcid.org/0000-0002-1694-233X ",
        ],
    )
    def test_normalize(self, value):
        assert normalize_orcid(value) == "0000-0002-1694-233X"

    @mark.parametrize(
        "value", ["0000-0002-1825-0098", "https://evil.org/0000-0002-1825-0097", ""]
    )
    def test_normalize_refuses(self, value):
        with raises(ValueError):
            normalize_orcid(value)

    def test_link_creates_researcher(self, db):
        _create_user(db, "link-a", "test", raise_on_error=False)
        researcher, created = link_orcid(db, "link-a", "0000-0001-5109-3700", "A")
        assert created
        assert researcher.orcid == "0000-0001-5109-3700"
        assert researcher.name == "A"
        assert find_users_for_orcid(db, "0000-0001-5109-3700") == ["link-a"]

    def test_link_reuses_researcher_written_as_url(self, db):
        Researcher = db.model.researcher
        existing = Researcher(name="B", orcid="https://orcid.org/0000-0002-9079-593X")
        db.session.add(existing)
        db.session.flush()
        _create_user(db, "link-b", "test", raise_on_error=False)
        researcher, created = link_orcid(db, "link-b", "0000-0002-9079-593X")
        assert not created
        assert researcher.id == existing.id
        assert find_users_for_orcid(db, "0000-0002-9079-593X") == ["link-b"]

    def test_link_fills_in_the_users_researcher(self, db):
        Researcher = db.model.researcher
        own = Researcher(name="C")
        db.session.add(own)
        db.session.flush()
        user = _create_user(db, "link-c", "test", raise_on_error=False)
        user.researcher_id = own.id
        db.session.commit()
        researcher, created = link_orcid(db, "link-c", "0000-0003-4580-4443")
        assert not created
        assert researcher.id == own.id
        assert researcher.orcid == "0000-0003-4580-4443"

    def test_link_refuses_a_second_user(self, db):
        _create_user(db, "link-d", "test", raise_on_error=False)
        with raises(AccountLinkError):
            link_orcid(db, "link-d", "0000-0001-5109-3700")
        assert find_users_for_orcid(db, "0000-0001-5109-3700") == ["link-a"]

    def test_link_refuses_unknown_user(self, db):
        with raises(AccountLinkError):
            link_orcid(db, "nobody-here", "0000-0001-5109-3700")


class TestOrcidUnavailable:
    def test_status_says_off(self, browser, use_orcid):
        use_orcid(None)
        data = browser.get("/api/v2/auth/status").json()
        assert data["login"] is False
        assert data["username"] is None
        assert data["orcid"] == {"enabled": False, "mode": None, "login_url": None}

    def test_routes_are_absent(self, browser, use_orcid):
        use_orcid(None)
        assert browser.get("/api/v2/auth/orcid/login").status_code == 404
        assert browser.get("/api/v2/auth/orcid/callback").status_code == 404


class TestDirectSignIn:
    @fixture(autouse=True)
    def direct(self, use_orcid, linked_user):
        transport = httpx2.MockTransport(fake_orcid)
        return use_orcid(orcid_sign_in_from_env(direct_env(), transport=transport))

    def test_status_offers_orcid(self, browser):
        data = browser.get("/api/v2/auth/status").json()
        assert data["orcid"] == {
            "enabled": True,
            "mode": "direct",
            "login_url": "/api/v2/auth/orcid/login",
        }
        assert CLIENT_SECRET not in browser.get("/api/v2/auth/status").text

    def test_login_redirects_to_orcid(self, browser):
        location, query = start_sign_in(browser)
        assert location.netloc == "orcid.org"
        assert query["client_id"] == ["APP-TEST"]
        assert query["redirect_uri"] == [REDIRECT_URI]
        assert "client_secret" not in query
        assert "orcid_state_cookie" in browser.cookies

    def test_linked_user_signs_in(self, browser):
        res = sign_in_directly(browser, "linked")
        assert res.status_code == 307
        assert res.headers["location"] == "/projects"
        assert "orcid_state_cookie" not in browser.cookies
        assert is_session(browser)

    def test_session_refreshes(self, browser):
        sign_in_directly(browser, "linked")
        res = browser.post("/api/v2/auth/refresh")
        assert res.json()["username"] == USERNAME

    def test_unlinked_user_is_refused(self, browser):
        res = sign_in_directly(browser, "unlinked")
        assert res.status_code == 403
        assert UNLINKED in res.json()["error"]["detail"]
        assert "access_token_cookie" not in browser.cookies

    def test_bad_code_is_refused(self, browser):
        assert sign_in_directly(browser, "forged").status_code == 400
        assert not is_session(browser)

    def test_state_must_match_cookie(self, browser):
        _, query = start_sign_in(browser)
        browser.cookies.clear()
        res = browser.get(
            "/api/v2/auth/orcid/callback",
            params={"code": "linked", "state": query["state"][0]},
        )
        assert res.status_code == 400

    def test_forged_state_is_refused(self, browser):
        start_sign_in(browser)
        res = browser.get(
            "/api/v2/auth/orcid/callback", params={"code": "linked", "state": "x"}
        )
        assert res.status_code == 400

    def test_cancelled_sign_in(self, browser):
        _, query = start_sign_in(browser)
        res = browser.get(
            "/api/v2/auth/orcid/callback",
            params={"error": "access_denied", "state": query["state"][0]},
        )
        assert res.status_code == 400

    @mark.parametrize(
        "return_url", ["https://evil.example.com/", "//evil.example.com", "evil"]
    )
    def test_return_url_stays_on_site(self, browser, return_url):
        _, query = start_sign_in(browser, return_url)
        res = browser.get(
            "/api/v2/auth/orcid/callback",
            params={"code": "linked", "state": query["state"][0]},
        )
        assert res.headers["location"] == "/"


class TestBrokerSignIn:
    @fixture(autouse=True)
    def broker(self, use_orcid, linked_user):
        transport = httpx2.MockTransport(fake_broker)
        return use_orcid(orcid_sign_in_from_env(broker_env(), transport=transport))

    def test_status_offers_orcid(self, browser):
        assert browser.get("/api/v2/auth/status").json()["orcid"]["mode"] == "broker"

    def test_login_redirects_to_broker(self, browser):
        location, query = start_sign_in(browser)
        assert f"{location.scheme}://{location.netloc}{location.path}" == (
            f"{BROKER}/login"
        )
        assert query["return_to"] == [REDIRECT_URI]
        assert len(query["state"][0]) > 0

    def test_valid_assertion_signs_in(self, browser):
        res = sign_in_with_broker(browser)
        assert res.status_code == 307
        assert res.headers["location"] == "/projects"
        assert is_session(browser)

    def test_assertion_with_url_form_id(self, browser):
        url_id = f"https://orcid.org/{LINKED}"
        res = sign_in_with_broker(browser, lambda s: assertion(s, sub=url_id))
        assert res.status_code == 307

    def test_unlinked_user_is_refused(self, browser):
        res = sign_in_with_broker(browser, lambda s: assertion(s, sub=UNLINKED))
        assert res.status_code == 403
        assert not is_session(browser)

    @mark.parametrize(
        "make_assertion",
        [
            lambda s: assertion(s, aud="https://other-lab.example.org"),
            lambda s: assertion(s, iss="https://impostor.example.org"),
            lambda s: assertion(
                s, iat=int(time.time()) - 600, exp=int(time.time()) - 300
            ),
            lambda s: assertion(s, key=Ed25519PrivateKey.generate()),
            lambda s: assertion(s, key="k" * 32, algorithm="HS256"),
            lambda s: assertion(s, kid="unknown-key"),
            lambda s: assertion(s, state="another-sign-in"),
            lambda s: assertion(s, jti=None),
            lambda s: "not-a-token",
        ],
        ids=[
            "wrong-aud",
            "wrong-iss",
            "expired",
            "bad-signature",
            "wrong-alg",
            "unknown-kid",
            "wrong-state",
            "no-jti",
            "malformed",
        ],
    )
    def test_bad_assertion_is_refused(self, browser, make_assertion):
        res = sign_in_with_broker(browser, make_assertion)
        assert res.status_code == 400
        assert not is_session(browser)

    def test_state_must_match_cookie(self, browser):
        _, query = start_sign_in(browser)
        state = query["state"][0]
        browser.cookies.clear()
        res = browser.get(
            "/api/v2/auth/orcid/callback",
            params={"assertion": assertion(state), "state": state},
        )
        assert res.status_code == 400

    def test_assertion_is_single_use(self, broker):
        token = assertion("some-state")
        source = broker.source
        claims = asyncio.run(source.verify(token, "some-state"))
        assert claims["sub"] == LINKED
        with raises(Exception) as err:
            asyncio.run(source.verify(token, "some-state"))
        assert err.value.status_code == 400
