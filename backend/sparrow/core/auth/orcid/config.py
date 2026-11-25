from os import environ
from typing import Mapping

import httpx2
from macrostrat.auth_system.session import AuthSettings

from sparrow.logs import get_logger

from .sources import BrokerIdentitySource, DirectIdentitySource, IdentitySource

log = get_logger(__name__)

# Fixed by the gateway, which serves the API at the root of the lab's domain
CALLBACK_PATH = "/api/v2/auth/orcid/callback"
# Keeps state tokens from being accepted as anything else signed with the lab's key
STATE_AUDIENCE = "sparrow-orcid-state"


class OrcidSignIn:
    """ORCID sign-in as a lab has configured it."""

    def __init__(self, settings: AuthSettings, source: IdentitySource):
        self.settings = settings
        self.source = source

    @property
    def mode(self) -> str:
        return self.source.mode


def orcid_sign_in_from_env(
    env: Mapping[str, str] | None = None,
    transport: httpx2.AsyncBaseTransport | None = None,
) -> OrcidSignIn | None:
    """ORCID sign-in from the lab's environment, or None when it is not set up.
    A lab's own ORCID client wins over a broker."""
    env = environ if env is None else env
    client_id = env.get("SPARROW_ORCID_CLIENT_ID")
    client_secret = env.get("SPARROW_ORCID_CLIENT_SECRET")
    broker_url = env.get("SPARROW_ORCID_BROKER_URL")

    if bool(client_id) != bool(client_secret):
        log.warning(
            "ORCID sign-in needs both SPARROW_ORCID_CLIENT_ID "
            "and SPARROW_ORCID_CLIENT_SECRET"
        )
    direct = bool(client_id and client_secret)
    if not direct and not broker_url:
        return None

    redirect_uri = lab_redirect_uri(env)
    if redirect_uri is None:
        log.warning(
            "ORCID sign-in is configured, but the lab's public address is unknown. "
            "Set SPARROW_DOMAIN or SPARROW_ORCID_REDIRECT_URI."
        )
        return None

    params = dict(
        secret_key=env.get("SPARROW_SECRET_KEY", ""),
        audience=STATE_AUDIENCE,
        oauth_client_id=client_id or "",
        oauth_client_secret=client_secret or "",
        redirect_uri=redirect_uri,
        state_cookie="orcid_state_cookie",
        default_return_url=env.get("SPARROW_BASE_URL") or "/",
    )
    base_url = env.get("SPARROW_ORCID_BASE_URL")
    if base_url:
        base_url = base_url.rstrip("/")
        params.update(
            oauth_authorization_url=f"{base_url}/authorize",
            oauth_token_url=f"{base_url}/token",
            oauth_userinfo_url=f"{base_url}/userinfo",
        )
    settings = AuthSettings(**params)

    if direct:
        return OrcidSignIn(settings, DirectIdentitySource(settings, transport))
    return OrcidSignIn(settings, BrokerIdentitySource(broker_url, settings, transport))


def lab_redirect_uri(env: Mapping[str, str]) -> str | None:
    """The lab's callback URL: set explicitly, or built from its HTTPS domain."""
    explicit = env.get("SPARROW_ORCID_REDIRECT_URI")
    if explicit:
        return explicit
    domain = env.get("SPARROW_DOMAIN")
    if not domain:
        return None
    port = env.get("SPARROW_HTTPS_PORT")
    if port and port != "443":
        domain = f"{domain}:{port}"
    return f"https://{domain}{CALLBACK_PATH}"
