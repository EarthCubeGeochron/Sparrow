from setuptools import setup

setup(
    name="sparrow",
    version="0.1",
    # Currently these package directories don't appear to be used
    # to actually install the files.
    package_dir={"sparrow": "sparrow", "core_plugins": "plugins"},
    entry_points={"console_scripts": ["sparrow = sparrow.cli:cli"]},
)
