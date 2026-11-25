"""Where a lab learns who signed in: from ORCID itself (direct) or from an
identity broker's signed assertion (broker)."""

import asyncio
import secrets
import time
from typing import Mapping, Protocol
from urllib.parse import urlencode

import httpx2
import jwt
from macrostrat.auth_system.session import AuthSettings, OAuthIdentity
from macrostrat.auth_system.session.router import fetch_identity
from starlette.exceptions import HTTPException

# The only algorithm a broker may sign with; anything else is refused unread
BROKER_ALGORITHM = "EdDSA"


class IdentitySource(Protocol):
    mode: str

    def authorization_url(self, state: str) -> str:
        """Where the browser goes to sign in."""
        ...

    async def identify(self, params: Mapping[str, str], state: str) -> OAuthIdentity:
        """The identity carried back to the lab's callback."""
        ...


class DirectIdentitySource:
    """The lab holds its own ORCID client and exchanges the code itself."""

    mode = "direct"

    def __init__(
        self, settings: AuthSettings, transport: httpx2.AsyncBaseTransport = None
    ):
        self.settings = settings
        self.transport = transport

    def authorization_url(self, state: str) -> str:
        params = {
            "scope": self.settings.oauth_scope,
            "client_id": self.settings.oauth_client_id,
            "response_type": "code",
            "redirect_uri": self.settings.redirect_uri,
            "state": state,
        }
        return f"{self.settings.oauth_authorization_url}?{urlencode(params)}"

    async def identify(self, params: Mapping[str, str], state: str) -> OAuthIdentity:
        code = params.get("code")
        if not code:
            raise HTTPException(400, "ORCID returned no sign-in code")
        try:
            return await fetch_identity(self.settings, code, self.transport)
        except httpx2.HTTPError:
            raise HTTPException(502, "Could not reach ORCID") from None


class BrokerIdentitySource:
    """An identity broker holds the ORCID client and asserts who signed in."""

    mode = "broker"

    def __init__(
        self,
        broker_url: str,
        settings: AuthSettings,
        transport: httpx2.AsyncBaseTransport = None,
    ):
        self.broker_url = broker_url.rstrip("/")
        self.settings = settings
        self.keys = BrokerKeys(f"{self.broker_url}/.well-known/jwks.json", transport)
        self.seen = ReplayCache()

    def authorization_url(self, state: str) -> str:
        params = {"return_to": self.settings.redirect_uri, "state": state}
        return f"{self.broker_url}/login?{urlencode(params)}"

    async def identify(self, params: Mapping[str, str], state: str) -> OAuthIdentity:
        assertion = params.get("assertion")
        if not assertion:
            raise HTTPException(400, "The identity broker returned no assertion")
        claims = await self.verify(assertion, state)
        return OAuthIdentity(sub=claims["sub"], name=claims.get("name") or "")

    async def verify(self, assertion: str, state: str) -> dict:
        refused = HTTPException(400, "The identity assertion was not accepted")
        try:
            header = jwt.get_unverified_header(assertion)
        except jwt.PyJWTError:
            raise refused from None
        if header.get("alg") != BROKER_ALGORITHM:
            raise refused
        key = await self.keys.get(header.get("kid"))
        if key is None:
            raise refused
        try:
            claims = jwt.decode(
                assertion,
                key,
                algorithms=[BROKER_ALGORITHM],
                audience=self.settings.origin,
                issuer=self.broker_url,
                options={"require": ["exp", "iat", "iss", "aud", "sub", "jti"]},
            )
        except jwt.PyJWTError:
            raise refused from None
        # Binds the assertion to this browser's sign-in, so a leaked one is useless
        if not secrets.compare_digest(str(claims.get("state", "")), state):
            raise refused
        if not self.seen.add(claims["jti"], claims["exp"]):
            raise refused
        return claims


class BrokerKeys:
    """The broker's public keys, fetched from its JWKS and refetched when an
    assertion names a key not yet seen."""

    max_age = 3600
    # Bounds how often unknown key ids can make the lab call the broker
    min_refetch_interval = 30

    def __init__(self, url: str, transport: httpx2.AsyncBaseTransport = None):
        self.url = url
        self.transport = transport
        self._keys = {}
        self._fetched = None
        self._lock = asyncio.Lock()

    async def get(self, kid: str | None):
        if not kid:
            return None
        async with self._lock:
            age = None if self._fetched is None else time.monotonic() - self._fetched
            if age is None or age > self.max_age:
                await self._fetch()
            elif kid not in self._keys and age > self.min_refetch_interval:
                await self._fetch()
        return self._keys.get(kid)

    async def _fetch(self):
        try:
            async with httpx2.AsyncClient(transport=self.transport, timeout=10) as c:
                res = await c.get(self.url)
            res.raise_for_status()
            jwks = jwt.PyJWKSet.from_dict(res.json())
        except (httpx2.HTTPError, ValueError, jwt.PyJWTError):
            raise HTTPException(502, "Could not read the identity broker's keys")
        self._keys = {
            k.key_id: k.key
            for k in jwks.keys
            if k.key_id and k.algorithm_name == BROKER_ALGORITHM
        }
        self._fetched = time.monotonic()


class ReplayCache:
    """Assertion ids already used, kept until they expire."""

    def __init__(self):
        self._seen: dict[str, float] = {}

    def add(self, jti: str, exp: float) -> bool:
        now = time.time()
        self._seen = {k: v for k, v in self._seen.items() if v > now}
        if jti in self._seen:
            return False
        self._seen[jti] = exp
        return True
