from setuptools import setup

setup(
    name="sparrow",
    version="1.6.0",
    # Currently these package directories don't appear to be used
    # to actually install the files.
    packages=["sparrow", "sparrow_tests"],
    package_dir={
        "sparrow": "sparrow",
        "core_plugins": "plugins",
        "sparrow_tests": "sparrow_tests",
        "sparrow_worker": "sparrow_worker",
    },
    entry_points={"console_scripts": ["sparrow = sparrow.cli:cli"]},
)
