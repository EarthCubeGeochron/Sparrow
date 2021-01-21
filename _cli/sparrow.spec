# -*- mode: python ; coding: utf-8 -*-
from os import path

block_cipher = None

spec_path = path.abspath(SPECPATH)
src_root = path.abspath(path.join(spec_path, ".."))
src_excludes = [
    "_cli",
    ".pytest_cache",
    "docs",
    ".git",
    ".githooks",
    ".github",
    "frontend/node_modules",
]


a = Analysis(
    ["sparrow_cli/__main__.py"],
    pathex=[spec_path],
    binaries=[],
    datas=[],
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
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    Tree(src_root, prefix="srcroot", excludes=src_excludes),
    strip=False,
    upx=True,
    upx_exclude=[],
    name="sparrow",
)
