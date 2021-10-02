from itertools import groupby
from packaging.version import Version, InvalidVersion

from ..util import cmd, SparrowCommandError


def all_equal(*items):
    g = groupby(items)
    return next(g, True) and not next(g, False)


def remove_postrelease(version):
    spec = Version(version)
    while spec.is_postrelease:
        version = version[:-1]
        try:
            spec = Version(version)
        except InvalidVersion:
            pass
    return version


def clean_tag(tag):
    tag = tag.replace("refs/tags/", "")
    if tag.startswith("v"):
        tag = tag[1:]
    return tag


def check_version_exists(version):
    tag_name = "v" + version
    res = cmd("git tag -l", tag_name, capture_output=True)
    return bool(res.stdout.strip())


def check_output(*args, **kwargs):
    res = cmd(*args, capture_output=True, **kwargs)
    if res.returncode != 0:
        raise SparrowCommandError("Command failed", res.stderr.decode())
    output = res.stdout.decode("utf-8").strip()
    if output.isspace():
        return None
    return output
