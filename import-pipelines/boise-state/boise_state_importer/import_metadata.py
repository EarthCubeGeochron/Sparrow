from requests import get
from click import echo
from sparrow.database import Database
from sqlalchemy.sql import select
from sqlalchemy.dialects.postgresql import insert

def get_data(uri):
    h = {"Accept":"application/json"}
    return get(uri, headers=h).json()

def import_igsn(db, igsn, force=False):
    echo(igsn, color='green')
    tbl = db.table.igsn_data

    model = db.get('igsn_data', igsn)
    if model and not force:
        return

    url = f"https://app.geosamples.org/sample/igsn/{igsn}"
    data = get_data(url)

    cols = dict(data=data)
    sql = (insert(tbl)
        .values(igsn=igsn, **cols)
        .on_conflict_do_update(
            index_elements=['igsn'],
            set_=cols))

    db.session.execute(sql)
    db.session.commit()

def import_metadata():
    """
    Import IGSN metadata from SESAR
    """
    db = Database()
    echo("Requesting list of samples from SESAR")
    next_list = "https://app.geosamples.org/samples/user_code/BSU?limit=100"
    while next_list is not None:
        data = get_data(next_list)
        for igsn in data['igsn_list']:
            import_igsn(db, igsn)
        next_list = data.get('next_list', None)
