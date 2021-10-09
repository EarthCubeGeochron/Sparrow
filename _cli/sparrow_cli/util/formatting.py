import re
import sys
from os import path
from click import style
from rich.console import Console

console = Console(file=sys.stderr, highlight=False)


def format_config_path(cfg):
    """A helper for pretty formatting a path,
    eliding most of the directory tree.
    """
    home = path.expanduser("~")
    if cfg.startswith(home):
        cfg = cfg.replace(home, "~")
    split_path = cfg.split("/")
    tokens = []
    for i, token in enumerate(split_path):
        n_c = len(token)
        if i < len(split_path) - 2:
            tokens.append(token[0 : min(2, n_c)])
        else:
            tokens.append(token)
    return path.join(*tokens)


def format_description(desc):
    desc = re.sub("\[\[(.*?)\]\]", style("\\1", fg="red", bold=True), desc)
    desc = re.sub("\[(.*?)\]", style("\\1", fg="green", bold=True), desc)
    return re.sub("`(.*?)`", style("\\1", fg="cyan"), desc)
