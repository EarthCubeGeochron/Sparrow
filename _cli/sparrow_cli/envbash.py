from __future__ import absolute_import, unicode_literals

import os
import pipes
import subprocess
import sys


try:
    FileNotFoundError
except NameError:
    # Python 2
    FileNotFoundError = IOError


FIXUPS = ["_", "OLDPWD", "PWD", "SHLVL"]


def read_envbash(
    envbash, bash="bash", env=os.environ, missing_ok=False, fixups=None, args=None
):
    """
    Source ``envbash`` and return the resulting environment as a dictionary.
    """
    # make sure the file exists and is readable.
    # alternatively we could test os.access (especially on Python 3.3+ with
    # effective_ids) but this approach raises FileNotFoundError or
    # PermissionError which is what we want.
    try:
        with open(envbash):
            pass
    except FileNotFoundError:
        if missing_ok:
            return
        raise

    # quote args since they will be interpreted by shell
    quoted_args = " ".join(pipes.quote(x) for x in args or [])

    # construct an inline script which sources env.bash then prints the
    # resulting environment so it can be eval'd back into this process.
    inline = """
        set -a
        source {} {} >/dev/null
        {} -c "import os; print(repr(dict(os.environ)))"
    """.format(
        pipes.quote(envbash), quoted_args, pipes.quote(sys.executable)
    )

    print("Running envbash")

    # run the inline script with bash -c, capturing stdout. if there is any
    # error output from env.bash, it will pass through to stderr.
    # exit status is ignored.
    with open(os.devnull) as null:
        output, _ = subprocess.Popen(
            [bash, "-c", inline],
            stdin=null,
            stdout=subprocess.PIPE,
            stderr=None,
            bufsize=-1,
            close_fds=True,
            env=env,
        ).communicate()

    print("Done running envbash")

    # the only stdout from the inline script should be
    # print(repr(dict(os.environ))) so there should be no syntax errors
    # eval'ing this. however there will be no output to eval if the sourced
    # env.bash exited early, and that indicates script failure.
    if not output:
        raise ValueError("{} exited early".format(envbash))

    # the eval'd output should return a dictionary.
    nenv = eval(output)

    # there are a few environment variables that vary between this process and
    # running the inline script with bash -c, but are certainly not part of the
    # intentional settings in env.bash.
    if fixups is None:
        fixups = FIXUPS
    for f in fixups:
        if f in env:
            nenv[f] = env[f]
        elif f in nenv:
            del nenv[f]

    # work around PEP 538
    # https://www.python.org/dev/peps/pep-0538/#explicitly-setting-lc-ctype-for-utf-8-locale-coercion
    if (
        sys.version_info > (3, 6)
        and env is not os.environ
        and nenv.get("LC_CTYPE") == "C.UTF-8"
    ):
        del nenv["LC_CTYPE"]

    return nenv


def load_envbash(envbash, into=os.environ, override=False, remove=False, **kwargs):
    """
    Load ``envbash`` into ``into`` (default ``os.environ``).
    """
    loaded = read_envbash(envbash, **kwargs)
    if loaded is not None:
        if remove:
            for k in set(into) - set(loaded):
                del into[k]
        if override:
            into.update(loaded)
        else:
            for k in set(loaded) - set(into):
                into[k] = loaded[k]