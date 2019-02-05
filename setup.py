from setuptools import setup

setup(
    name='labdata',
    version='0.1',
    package_dir={'labdata': 'labdata'},
    entry_points={
          'console_scripts': ['labdata = labdata.cli:cli']
    },
)
