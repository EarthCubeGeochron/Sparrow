from os import path


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