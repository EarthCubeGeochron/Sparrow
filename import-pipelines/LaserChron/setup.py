from setuptools import setup

setup(
    name='labdata_laserchron_import',
    version='0.1',
    package_dir={'labdata_laserchron_import': 'labdata_laserchron_import'},
    install_requires=['sqlalchemy', 'h5py', 'click', 'click_plugins'],
    entry_points='''
        [labdata.plugins]
        import-e2=labdata_laserchron_import.cli:cli
    '''
)
