# -*- mode: python ; coding: utf-8 -*-
from os import path
from macrostrat.utils.shell import git_revision_info
from importlib import import_module

from PyInstaller.utils.hooks import collect_all

block_cipher = None

spec_path = path.abspath(SPECPATH)
src_root = path.abspath(path.join(spec_path, ".."))

revfile = path.join(SPECPATH, "build", "GIT_REVISION")
with open(revfile, "w") as f:
    # almost the same as `git rev-parse HEAD` but with `-dirty` suffix
    # https://stackoverflow.com/questions/21017300/git-command-to-get-head-sha1-with-dirty-suffix-if-workspace-is-not-clean
    git_revision_info(stdout=f)


data_files = {revfile: "."}

# Administrative commands run inside the bundle. The application's own code is
# read from the source tree bundled below (it carries SQL and other data
# files); what it depends on is collected here.
admin_dependencies = [
    "sqlalchemy", "geoalchemy2", "sqlalchemy_utils", "psycopg", "psycopg2",
    "macrostrat", "results", "pglast", "sqlparse", "shapely",
    "marshmallow", "marshmallow_sqlalchemy", "marshmallow_jsonschema", "stringcase",
    "starlette", "werkzeug", "jwt", "boto3", "botocore", "toposort",
    "celery", "kombu", "redis", "broadcaster", "requests", "aiofiles",
    "typer", "pydantic", "httpx", "multipart",
]
admin_datas, admin_binaries, admin_hiddenimports = [], [], []
for name in admin_dependencies:
    try:
        datas, binaries, hiddenimports = collect_all(name)
    except Exception:
        continue
    admin_datas += datas
    admin_binaries += binaries
    admin_hiddenimports += hiddenimports


a = Analysis(
    ["sparrow_cli/__main__.py"],
    pathex=[spec_path],
    binaries=admin_binaries,
    datas=[*data_files.items(), *admin_datas],
    hiddenimports=admin_hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="sparrow",
    strip=False,
    upx=True,
    console=True,
    debug=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    # Right now we include the entire source directory as a tree,
    # for easy correspondence with the source build.
    # Eventually, we will rely more on pre-compiled Docker
    # images, and we will have less need to carry around the source code.
    Tree(
        src_root,
        prefix="srcroot",
        excludes=[
            ".pytest_cache",
            "docs",
            ".git",
            ".githooks",
            ".github",
            "frontend",
            ".venv",
            "build",
            "dist",
            "__pycache__",
            "node_modules",
        ],
    ),
    # We have to include subfolders as separate trees, apparently, to allow
    # excluding of certain files.
    Tree(
        path.join(src_root, "frontend"),
        prefix="srcroot/frontend",
        excludes=["node_modules", "examples", ".parcel-cache"],
    ),
    Tree(
        path.join(src_root, "_cli"),
        prefix="srcroot/_cli",
        excludes=["build", "dist", ".venv"],
    ),
    strip=False,
    upx=True,
    upx_exclude=[],
    name="sparrow",
)
