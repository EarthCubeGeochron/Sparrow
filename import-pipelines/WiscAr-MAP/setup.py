from setuptools import setup

setup(
    name='labdata_wiscar_map_import',
    version='0.1',
    package_dir={'labdata_wiscar_map_import': 'pipeline'},
    install_requires=['sqlalchemy', 'pandas', 'click', 'click_plugins'],
    entry_points='''
        [labdata.plugins]
        import-map=pipeline.cli:cli
    '''
)
