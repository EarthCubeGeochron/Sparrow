import os
import re
import subprocess
from itertools import groupby
from .json_transformer import PyChronJSONImporter

# Find IA files by regex
iare = re.compile("(?P<cnt>_\d{5}\.ia\.json)")


def key(x):
    return "_".join(x.split("_")[:-1])


def counterkey(x):
    cnt = iare.search(x).group("cnt")
    # re returns cnt in form '_00000.ia.json'
    cnt = cnt.split(".")[0][1:]
    return int(cnt)


class PyChronRepoCrawler:
    def __init__(self, names, remote):
        local_repos_root = os.path.join(os.path.expanduser("~"), "local_repo")
        if not os.path.isdir(local_repos_root):
            os.mkdir(local_repos_root)

        self._local_root = local_repos_root
        if not isinstance(names, (list, tuple)):
            names = (names,)

        self._names = names
        self._remote = remote

    def scan(self):
        for name in self._names:
            print("scanning repo. {}".format(name))
            self.scan_repo(name)

    def scan_repo(self, name):
        # check if repo exists
        # clone otherwise
        root = os.path.join(self._local_root, name)
        if not os.path.isdir(root):
            url = "{}/{}".format(self._remote, name)
            subprocess.run(["git", "clone", url, root])

        importer = PyChronJSONImporter()

        # scan repo looking for ia files
        for d, ds, fs in os.walk(root):
            ias = [fi for fi in fs if iare.search(fi)]
            # only import the latest ia file for each group

            b = os.path.basename(os.path.dirname(d))
            for gi, gs in groupby(sorted(ias, key=key), key=key):
                uid = "{}{}".format(b, gi)
                # sort group by the counter suffix
                gs = sorted(gs, key=counterkey, reverse=True)
                p = os.path.join(d, gs[0])

                print("importing id={} file. {}".format(uid, p))
                importer.import_file(p)


if __name__ == "__main__":
    name = "NOB-Unknowns"
    remote = "https://github.com/WiscArData"
    pr = PyChronRepoCrawler(name, remote)
    pr.scan()
