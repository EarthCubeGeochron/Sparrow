import secrets
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from uuid import uuid4

import httpx2
import jwt
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from macrostrat.auth_system.session.cookies import set_state_cookie
from macrostrat.auth_system.session.router import fetch_identity
from macrostrat.auth_system.session.tokens import decode_token

from .settings import BrokerSettings

ALGORITHM = "EdDSA"
ASSERTION_SECONDS = 120
STATE_MINUTES = 10


def create_app(
    settings: BrokerSettings, transport: httpx2.AsyncBaseTransport | None = None
) -> FastAPI:
    """The identity broker: signs in with ORCID on a lab's behalf and returns a
    signed assertion of who signed in."""
    oauth = settings.oauth_settings()
    app = FastAPI(
        title="Sparrow identity broker", docs_url=None, redoc_url=None, openapi_url=None
    )

    @app.get("/")
    def index():
        return {
            "service": "Sparrow identity broker",
            "issuer": settings.url,
            "jwks_uri": f"{settings.url}/.well-known/jwks.json",
        }

    @app.get("/.well-known/jwks.json")
    def jwks():
        return {"keys": [settings.public_jwk]}

    @app.get("/login")
    def login(return_to: str, state: str):
        if settings.lab_origin(return_to) is None:
            raise HTTPException(400, "This return address may not use the broker")
        if not state or len(state) > 2048:
            raise HTTPException(400, "A lab state of at most 2048 characters is needed")
        nonce = secrets.token_urlsafe(24)
        token = _encode_state(oauth, nonce, return_to, state)
        params = {
            "scope": oauth.oauth_scope,
            "client_id": oauth.oauth_client_id,
            "response_type": "code",
            "redirect_uri": oauth.redirect_uri,
            "state": token,
        }
        response = RedirectResponse(
            f"{oauth.oauth_authorization_url}?{urlencode(params)}"
        )
        set_state_cookie(oauth, response, nonce)
        return response

    @app.get("/callback")
    async def callback(
        request: Request,
        state: str = "",
        code: str | None = None,
        error: str | None = None,
    ):
        claims = decode_token(oauth, state)
        nonce = request.cookies.get(oauth.state_cookie)
        if (
            claims is None
            or claims.get("type") != "broker-state"
            or not nonce
            or not secrets.compare_digest(str(claims.get("nonce", "")), nonce)
        ):
            raise HTTPException(400, "Sign-in state did not match")
        return_to = claims["return_to"]
        lab_state = claims["lab_state"]
        origin = settings.lab_origin(return_to)
        if origin is None:
            raise HTTPException(400, "This return address may not use the broker")

        if error or not code:
            reason = "access_denied" if error == "access_denied" else "sign_in_failed"
            params = {"error": reason, "state": lab_state}
        else:
            try:
                identity = await fetch_identity(oauth, code, transport)
            except httpx2.HTTPError:
                raise HTTPException(502, "Could not reach ORCID") from None
            assertion = _sign_assertion(settings, origin, identity, lab_state)
            params = {"assertion": assertion, "state": lab_state}

        response = RedirectResponse(f"{return_to}?{urlencode(params)}")
        response.delete_cookie(oauth.state_cookie)
        return response

    return app


def _sign_assertion(settings: BrokerSettings, audience: str, identity, lab_state):
    now = int(time.time())
    claims = {
        "iss": settings.url,
        "aud": audience,
        "sub": identity.sub,
        "name": identity.name,
        "iat": now,
        "exp": now + ASSERTION_SECONDS,
        "jti": uuid4().hex,
        "state": lab_state,
    }
    return jwt.encode(
        claims, settings.signing_key, algorithm=ALGORITHM, headers={"kid": settings.kid}
    )


def _encode_state(oauth, nonce: str, return_to: str, lab_state: str) -> str:
    claims = {
        "type": "broker-state",
        "nonce": nonce,
        "return_to": return_to,
        "lab_state": lab_state,
        "aud": oauth.audience,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=STATE_MINUTES),
    }
    return jwt.encode(claims, oauth.secret_key, algorithm=oauth.algorithm)
