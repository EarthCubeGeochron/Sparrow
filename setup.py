from setuptools import setup

setup(
    name='labdata',
    version='0.1',
    package_dir={'labdata': 'labdata'},
    install_requires=['sqlalchemy', 'pandas','flask','click', 'click_plugins'],
    entry_points={
          'console_scripts': ['labdata = labdata.cli:cli']
    },
)
