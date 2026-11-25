import base64
import hashlib
import json
from dataclasses import dataclass, field
from os import environ
from pathlib import Path
from typing import Mapping
from urllib.parse import urlparse

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from macrostrat.auth_system.session import AuthSettings
from macrostrat.auth_system.session.settings import ORCID_BASE_URL

# The path every lab serves its ORCID callback at
LAB_CALLBACK_PATH = "/api/v2/auth/orcid/callback"


class BrokerConfigError(ValueError):
    pass


@dataclass
class BrokerSettings:
    """What the broker needs to run. Secrets are kept out of its repr."""

    url: str
    orcid_client_id: str
    orcid_client_secret: str = field(repr=False)
    signing_key: Ed25519PrivateKey = field(repr=False)
    # Lab origins that may receive assertions; empty allows any that pass the checks
    allowed_origins: list[str] = field(default_factory=list)
    orcid_base_url: str = ORCID_BASE_URL

    def __post_init__(self):
        self.url = self.url.rstrip("/")
        self.orcid_base_url = self.orcid_base_url.rstrip("/")
        self.allowed_origins = [o.rstrip("/").lower() for o in self.allowed_origins]

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None):
        env = environ if env is None else env
        required = (
            "SPARROW_BROKER_URL",
            "SPARROW_BROKER_ORCID_CLIENT_ID",
            "SPARROW_BROKER_ORCID_CLIENT_SECRET",
        )
        missing = [k for k in required if not env.get(k)]
        if missing:
            raise BrokerConfigError(f"Set {', '.join(missing)}")

        pem = env.get("SPARROW_BROKER_SIGNING_KEY")
        key_file = env.get("SPARROW_BROKER_SIGNING_KEY_FILE")
        if not pem and key_file:
            pem = Path(key_file).read_text()
        if not pem:
            raise BrokerConfigError(
                "Set SPARROW_BROKER_SIGNING_KEY or SPARROW_BROKER_SIGNING_KEY_FILE"
            )

        origins = env.get("SPARROW_BROKER_ALLOWED_ORIGINS", "")
        return cls(
            url=env["SPARROW_BROKER_URL"],
            orcid_client_id=env["SPARROW_BROKER_ORCID_CLIENT_ID"],
            orcid_client_secret=env["SPARROW_BROKER_ORCID_CLIENT_SECRET"],
            signing_key=load_signing_key(pem),
            allowed_origins=[o.strip() for o in origins.split(",") if o.strip()],
            orcid_base_url=env.get("SPARROW_BROKER_ORCID_BASE_URL") or ORCID_BASE_URL,
        )

    @property
    def callback_url(self) -> str:
        return f"{self.url}/callback"

    @property
    def public_jwk(self) -> dict:
        raw = self.signing_key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        jwk = {"kty": "OKP", "crv": "Ed25519", "x": _b64(raw)}
        return {**jwk, "kid": _thumbprint(jwk), "alg": "EdDSA", "use": "sig"}

    @property
    def kid(self) -> str:
        return self.public_jwk["kid"]

    def oauth_settings(self) -> AuthSettings:
        """ORCID exchange and the broker's own state, in the shared library's terms."""
        return AuthSettings(
            secret_key=self._state_key(),
            audience="sparrow-broker-state",
            oauth_client_id=self.orcid_client_id,
            oauth_client_secret=self.orcid_client_secret,
            oauth_authorization_url=f"{self.orcid_base_url}/authorize",
            oauth_token_url=f"{self.orcid_base_url}/token",
            oauth_userinfo_url=f"{self.orcid_base_url}/userinfo",
            redirect_uri=self.callback_url,
            state_cookie="broker_state",
        )

    def _state_key(self) -> str:
        # Derived so no second secret is needed and state never uses the assertion key
        raw = self.signing_key.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption(),
        )
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"sparrow-broker-state",
        )
        return hkdf.derive(raw).hex()

    def lab_origin(self, return_to: str) -> str | None:
        """The origin of a lab callback URL the broker may send an assertion to."""
        if not isinstance(return_to, str) or len(return_to) > 2048:
            return None
        parsed = urlparse(return_to)
        host = parsed.hostname
        if host is None or parsed.username or parsed.password:
            return None
        if (
            parsed.query
            or parsed.fragment
            or not parsed.path.endswith(LAB_CALLBACK_PATH)
        ):
            return None
        if parsed.scheme not in ("http", "https"):
            return None
        if parsed.scheme == "http" and not _is_local(host):
            return None
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if self.allowed_origins and origin.lower() not in self.allowed_origins:
            return None
        return origin


def load_signing_key(pem: str | bytes) -> Ed25519PrivateKey:
    if isinstance(pem, str):
        pem = pem.encode()
    try:
        key = serialization.load_pem_private_key(pem, password=None)
    except (ValueError, TypeError):
        key = None
    if not isinstance(key, Ed25519PrivateKey):
        # The message never includes the value, which is a secret
        raise BrokerConfigError(
            "The broker's signing key must be an unencrypted Ed25519 private key in PEM form"
        )
    return key


def _is_local(host: str) -> bool:
    host = host.lower()
    return host in ("localhost", "127.0.0.1", "::1") or host.endswith(
        (".localhost", ".local")
    )


def _thumbprint(jwk: dict) -> str:
    # RFC 7638: SHA-256 over the required members, sorted, without whitespace
    canonical = json.dumps(jwk, sort_keys=True, separators=(",", ":"))
    return _b64(hashlib.sha256(canonical.encode()).digest())


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()
