"""ORCID sign-in for a lab, through its own ORCID client or an identity broker.

Either way, the lab ends the sign-in by issuing its usual session cookies, so the
frontend, PostgREST and token refresh see one token format.
"""

from .accounts import (
    AccountLinkError,
    find_users_for_orcid,
    link_orcid,
    normalize_orcid,
)
from .config import CALLBACK_PATH, OrcidSignIn, orcid_sign_in_from_env
from .routes import orcid_callback, orcid_login, orcid_status
from .sources import BrokerIdentitySource, DirectIdentitySource

__all__ = [
    "AccountLinkError",
    "BrokerIdentitySource",
    "CALLBACK_PATH",
    "DirectIdentitySource",
    "OrcidSignIn",
    "find_users_for_orcid",
    "link_orcid",
    "normalize_orcid",
    "orcid_callback",
    "orcid_login",
    "orcid_sign_in_from_env",
    "orcid_status",
]
