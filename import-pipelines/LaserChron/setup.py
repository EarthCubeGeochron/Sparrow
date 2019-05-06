from setuptools import setup

setup(
    name='sparrow_import_laserchron',
    version='0.1',
    package_dir={'sparrow_import_laserchron': 'sparrow_import_laserchron'},
    install_requires=['sqlalchemy', 'pandas', 'xlrd', 'click']
)
