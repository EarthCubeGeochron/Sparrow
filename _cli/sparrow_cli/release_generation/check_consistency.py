from os import path
from runpy import run_path
import json
from packaging.version import Version, InvalidVersion

from ..util import SparrowCommandError, console
from .util import check_version_exists, all_equal, check_output, clean_tag


def _check_consistency(version=None, exact=False):
    """Check the consistency of release information stored in the codebase"""
    latest_tag = check_output("git describe --tags --abbrev=0")
    current_rev = check_output("git describe --tags")
    if version is None:
        version = latest_tag

    version = clean_tag(version)

    # If we've provided a tag to check, then we clean it

    tag_name = "v" + version
    _exact_tag_match = all_equal(current_rev, latest_tag, tag_name)

    # Check that we have a valid PEP440 version specifier
    Version(version)

    key_ = "Version tag"
    if _exact_tag_match:
        key_ += " (exact)"
    console.print(f"{key_:28} v{version}")

    assert not version.startswith("v")

    assert check_version_exists(version)

    assert latest_tag == tag_name
    assert current_rev.startswith(tag_name)
    if exact:
        assert latest_tag == current_rev

    # Check backend version
    backend_meta = path.join("backend", "sparrow", "core", "meta.py")
    meta = run_path(backend_meta)
    _version = meta["__version__"]
    assert _version == version
    console.print(f"{backend_meta:29} {_version}")

    # Check base directory version file
    version_file = "sparrow-version.json"
    info = json.load(open(version_file, "r"))
    _version = info["core"]
    console.print(f"{version_file:29} {_version}")
    assert _version == version

    return tag_name


def check_consistency(tag_name=None, exact=False):
    try:
        tag_name = _check_consistency(tag_name, exact=exact)
    except AssertionError:
        raise SparrowCommandError(f"Version files are not consistent")
    except InvalidVersion:
        raise SparrowCommandError("Invalid version")
    console.print(f"Version information is consistent with tag {tag_name}")
