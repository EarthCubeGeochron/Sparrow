import secrets

from macrostrat.auth_system.session.cookies import set_state_cookie
from macrostrat.auth_system.session.tokens import create_state_token, decode_token
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse

from sparrow.core.context import get_database, get_sparrow_app

from .accounts import find_users_for_orcid, normalize_orcid
from .config import LOGIN_PATH, OrcidSignIn


async def orcid_login(request):
    """Start an ORCID sign-in, returning afterwards to `return_url`."""
    orcid = _require_orcid()
    settings = orcid.settings
    nonce = secrets.token_urlsafe(24)
    return_url = settings.safe_return_url(request.query_params.get("return_url"))
    state = create_state_token(settings, nonce, return_url)
    response = RedirectResponse(orcid.source.authorization_url(state))
    set_state_cookie(settings, response, nonce)
    return response


async def orcid_callback(request):
    """Finish an ORCID sign-in by issuing the lab's own session cookies."""
    from ..api import get_backend

    orcid = _require_orcid()
    settings = orcid.settings
    params = request.query_params
    state = params.get("state") or ""

    claims = decode_token(settings, state)
    nonce = request.cookies.get(settings.state_cookie)
    if (
        claims is None
        or claims.get("type") != "state"
        or not nonce
        or not secrets.compare_digest(str(claims.get("nonce", "")), nonce)
    ):
        raise HTTPException(400, "Sign-in state did not match")
    if params.get("error"):
        raise HTTPException(400, "ORCID sign-in was cancelled or refused")

    identity = await orcid.source.identify(params, state)
    try:
        orcid_id = normalize_orcid(identity.sub)
    except ValueError:
        raise HTTPException(400, "The identity provider returned no ORCID iD")

    usernames = find_users_for_orcid(get_database(), orcid_id)
    if len(usernames) == 0:
        raise HTTPException(
            403, f"ORCID iD {orcid_id} is not linked to a user of this lab"
        )
    if len(usernames) > 1:
        raise HTTPException(
            403, f"ORCID iD {orcid_id} is linked to more than one user of this lab"
        )

    response = RedirectResponse(settings.safe_return_url(claims.get("return_url")))
    get_backend().set_login_cookies(response, identity=usernames[0], role="admin")
    response.delete_cookie(settings.state_cookie)
    return response


def orcid_status() -> dict:
    """How the frontend can offer ORCID sign-in, if at all."""
    orcid = get_orcid()
    if orcid is None:
        return {"enabled": False, "mode": None, "login_url": None}
    return {"enabled": True, "mode": orcid.mode, "login_url": LOGIN_PATH}


def get_orcid() -> OrcidSignIn | None:
    return getattr(get_sparrow_app().plugins.get("auth"), "orcid", None)


def _require_orcid() -> OrcidSignIn:
    orcid = get_orcid()
    if orcid is None:
        raise HTTPException(404, "ORCID sign-in is not enabled for this lab")
    return orcid
