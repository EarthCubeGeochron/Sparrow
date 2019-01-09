from setuptools import setup

setup(
    name='labdata',
    version='0.1',
    package_dir={'labdata': 'labdata'},
    install_requires=['sqlalchemy', 'pandas']
)
