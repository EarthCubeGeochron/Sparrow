from setuptools import setup

setup(
    name='sparrow_wiscar_map_import',
    version='0.1',
    package_dir={'sparrow_wiscar_map_import': 'pipeline'},
    install_requires=['sqlalchemy', 'pandas', 'click', 'click_plugins'],
    entry_points='''
        [sparrow.plugins]
        import-map=pipeline.cli:cli
    '''
)
