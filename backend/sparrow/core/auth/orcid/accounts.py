"""Which Sparrow user an ORCID iD signs in as: the one linked to the researcher
with that iD. Accounts are never created by signing in."""

import re

from sqlalchemy import func

from sparrow.database.models import User

_orcid_url = re.compile(
    r"^(?:(?:https?://)?(?:www\.|sandbox\.)?orcid\.org/)?(\d{4}-\d{4}-\d{4}-\d{3}[\dX])/?$",
    re.IGNORECASE,
)
# Finds the iD inside a stored value, whether bare or written as a URL
_stored_orcid = "[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9Xx]"


class AccountLinkError(ValueError):
    pass


def find_users_for_orcid(db, orcid: str) -> list[str]:
    """Usernames of the users whose linked researcher has this ORCID iD."""
    bare = normalize_orcid(orcid)
    Researcher = db.model.researcher
    rows = (
        db.session.query(User.username)
        .join(Researcher, User.researcher_id == Researcher.id)
        .filter(_stored_form(Researcher.orcid) == bare)
        .order_by(User.username)
        .all()
    )
    return [r.username for r in rows]


def link_orcid(db, username: str, orcid: str, name: str | None = None):
    """Link a user to the researcher with an ORCID iD, creating or reusing that
    researcher. Returns the researcher and whether it was created."""
    bare = normalize_orcid(orcid)
    Researcher = db.model.researcher
    user = db.session.get(User, username)
    if user is None:
        raise AccountLinkError(f"No user named {username} exists")

    matches = (
        db.session.query(Researcher)
        .filter(_stored_form(Researcher.orcid) == bare)
        .order_by(Researcher.id)
        .all()
    )
    if len(matches) > 1:
        ids = ", ".join(str(r.id) for r in matches)
        raise AccountLinkError(f"Researchers {ids} all have ORCID iD {bare}")

    researcher = None
    if len(matches) == 1:
        researcher = matches[0]
    elif user.researcher_id is not None:
        current = db.session.get(Researcher, user.researcher_id)
        if current is not None and not current.orcid:
            researcher = current

    if researcher is not None:
        others = (
            db.session.query(User.username)
            .filter(User.researcher_id == researcher.id, User.username != username)
            .all()
        )
        if others:
            names = ", ".join(r.username for r in others)
            raise AccountLinkError(
                f"ORCID iD {bare} would also sign in as user {names}"
            )

    created = researcher is None
    if created:
        researcher = Researcher(name=name or username, orcid=bare)
        db.session.add(researcher)
        db.session.flush()
    elif not researcher.orcid:
        researcher.orcid = bare

    user.researcher_id = researcher.id
    db.session.add(user)
    db.session.commit()
    return researcher, created


def normalize_orcid(value: str) -> str:
    """The bare form of an ORCID iD (`0000-0002-1825-0097`), given bare or as a
    URL. Raises ValueError for anything that is not a valid iD."""
    match = _orcid_url.match(str(value).strip())
    if match is None:
        raise ValueError(f"{value!r} is not an ORCID iD")
    bare = match.group(1).upper()
    if _checksum(bare.replace("-", "")[:-1]) != bare[-1]:
        raise ValueError(f"{value!r} is not a valid ORCID iD (bad check digit)")
    return bare


def _checksum(digits: str) -> str:
    # ISO 7064 MOD 11-2, as ORCID specifies
    total = 0
    for d in digits:
        total = (total + int(d)) * 2
    result = (12 - total % 11) % 11
    return "X" if result == 10 else str(result)


def _stored_form(column):
    return func.upper(func.substring(column, _stored_orcid))
