from sys import exit
from os import environ, listdir, path
from datetime import datetime
from click import command, option, echo, secho, style
import sparrow
from sparrow.database import get_or_create
from sparrow.util import relative_path
from IPython import embed
from h5py import File

@command(name="import-e2")
@option('--test', is_flag=True, default=True)
def cli(test=True):
    """
    Import Matlab save file for E2 in bulk.
    """
    if not test:
        echo(f"Only test data supported for now")
        return
    fn = relative_path(__file__,'../test-data/Test_E2_Export.mat')
    print(fn)
    # Load file as a pre-7.3 matlab file
    mat = loadmat(fn)
    embed()

