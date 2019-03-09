from setuptools import setup

setup(
    name='sparrow',
    version='0.1',
    package_dir={'sparrow': 'sparrow'},
    entry_points={
          'console_scripts': ['sparrow = sparrow.cli:cli']
    },
)
