# -*- mode: python ; coding: utf-8 -*-
from os import path
from macrostrat.utils.shell import git_revision_info
from importlib import import_module

block_cipher = None

spec_path = path.abspath(SPECPATH)
src_root = path.abspath(path.join(spec_path, ".."))

revfile = path.join(SPECPATH, "build", "GIT_REVISION")
with open(revfile, "w") as f:
    # almost the same as `git rev-parse HEAD` but with `-dirty` suffix
    # https://stackoverflow.com/questions/21017300/git-command-to-get-head-sha1-with-dirty-suffix-if-workspace-is-not-clean
    git_revision_info(stdout=f)


data_files = {revfile: "."}

# Add data files needed by docker-compose
_compose_files = ["config/config_schema_v1.json", "config/compose_spec.json"]
compose_root = path.dirname(import_module("compose").__file__)
for fn in _compose_files:
    fullpath = path.join(compose_root, fn)
    data_files[fullpath] = "compose/config"

_schemainspect_root = path.dirname(import_module("schemainspect").__file__)
fullpath = path.join(_schemainspect_root, "pg", "sql")
data_files[fullpath] = "schemainspect/pg/sql"

a = Analysis(
    ["sparrow_cli/__main__.py"],
    pathex=[spec_path],
    binaries=[],
    datas=data_files.items(),
    hiddenimports=[],
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
