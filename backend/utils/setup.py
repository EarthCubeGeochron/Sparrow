from setuptools import setup

setup(
    name="sparrow_utils",
    version="1.6.0",
    # Currently these package directories don't appear to be used
    # to actually install the files.
    packages=["sparrow_utils"],
    package_dir={
        "sparrow_utils": "sparrow_utils",
    },
)