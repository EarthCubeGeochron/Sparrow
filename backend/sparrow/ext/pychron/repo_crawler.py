import os
import re
import subprocess
from itertools import groupby

# Find IA files by regex
iare = re.compile(r"(?P<cnt>_\d{5}\.ia\.json)")


def key(x):
    return "_".join(x.split("_")[:-1])


def counterkey(x):
    cnt = iare.search(x).group("cnt")
    # re returns cnt in form '_00000.ia.json'
    cnt = cnt.split(".")[0][1:]
    return int(cnt)


class PyChronRepoCrawler:
    def __init__(self, remote, names, local_root=None):
        if local_root is None:
            local_root = os.path.join(os.path.expanduser("~"), "local_repo")
        self._local_root = local_root

        if not os.path.isdir(self._local_root):
            os.mkdir(self._local_root)

        if not isinstance(names, (list, tuple)):
            names = (names,)

        self._names = names
        self._remote = remote

    def scan(self):
        for name in self._names:
            print(f"scanning repository {name}")
            yield from self.scan_repo(name)

    def scan_repo(self, name):
        # check if repo exists
        # clone otherwise
        root = os.path.join(self._local_root, name)
        url = f"{self._remote}/{name}"

        giturl = url + ".git"
        user = os.environ.get("GITHUB_USER", None)
        pat = os.environ.get("GITHUB_TOKEN", None)
        if user is not None and pat is not None:
            print(f"Logging in using github user {user} and personal access token")
            giturl = giturl.replace("https://", f"https://{user}:{pat}@")

        if not os.path.isdir(root):
            subprocess.run(["git", "clone", giturl, root])
        else:
            subprocess.run(["git", "remote", "set-url", "origin", giturl], cwd=root)
            subprocess.run(["git", "pull", "origin", "master"], cwd=root)

        # scan repo looking for ia files
        for d, ds, fs in os.walk(root):
            ias = [fi for fi in fs if iare.search(fi)]
            # only import the latest ia file for each group

            b = os.path.basename(os.path.dirname(d))
            for gi, gs in groupby(sorted(ias, key=key), key=key):
                uid = "{}{}".format(b, gi)
                # sort group by the counter suffix
                gs = sorted(gs, key=counterkey, reverse=True)
                local_path = os.path.join(d, gs[0])

                tail = local_path.split(root)[1]
                remote_url = f"{url}/blob/master{tail}"

                yield uid, local_path, remote_url
