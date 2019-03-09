from setuptools import setup

setup(
    name='sparrow_laserchron_import',
    version='0.1',
    package_dir={'sparrow_laserchron_import': 'sparrow_laserchron_import'},
    install_requires=['sqlalchemy', 'h5py', 'click', 'click_plugins'],
    entry_points='''
        [sparrow.plugins]
        import-e2=sparrow_laserchron_import.cli:cli
    '''
)
