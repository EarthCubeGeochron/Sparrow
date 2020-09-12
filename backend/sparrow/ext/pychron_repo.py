# ===============================================================================
# Copyright 2020 ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================
import os
import re
import subprocess
from itertools import groupby

try:
    from backend.sparrow.ext.pychron import PyChronJSONImporter
except ImportError:
    class PyChronJSONImporter:
        def import_file(self, *args, **kw):
            pass

iare = re.compile('(?P<cnt>_\d{5}\.ia\.json)')


def key(x):
    return '_'.join(x.split('_')[:-1])


def counterkey(x):
    cnt = iare.search(x).group('cnt')
    # re returns cnt in form '_00000.ia.json'
    cnt = cnt.split('.')[0][1:]
    return int(cnt)


class PychronRepo:
    def __init__(self, name, remote):
        local_repos_root = os.path.join(os.path.expanduser('~'), 'local_repo')
        if not os.path.isdir(local_repos_root):
            os.mkdir(local_repos_root)

        self._root = os.path.join(local_repos_root, name)
        self._url = '{}/{}'.format(remote, name)

    def scan(self):
        # check if repo exists
        # clone otherwise

        root = self._root
        if not os.path.isdir(root):
            subprocess.run(['git', 'clone', self._url, root])

        importer = PyChronJSONImporter()

        # scan repo looking for ia files
        for d, ds, fs in os.walk(root):
            ias = [fi for fi in fs if iare.search(fi)]
            # only import the latest ia file for each group

            b = os.path.basename(os.path.dirname(d))
            for gi, gs in groupby(sorted(ias, key=key), key=key):
                uid = '{}{}'.format(b, gi)
                # sort group by the counter suffix
                gs = sorted(gs, key=counterkey, reverse=True)
                p = os.path.join(d, gs[0])

                print('importing id={} file. {}'.format(uid, p))
                importer.import_file(p)


if __name__ == '__main__':
    name = 'NOB-Unknowns'
    remote = 'https://github.com/WiscArData'
    pr = PychronRepo(name, remote)
    pr.scan()

# ============= EOF =============================================
