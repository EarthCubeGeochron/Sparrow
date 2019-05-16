from lxml.etree import tostring
from itertools import chain
from sparrow.import_helpers import BaseImporter, SparrowImportError
from datetime import datetime
from io import StringIO
from pandas import read_csv, concat
from math import isnan
from sqlalchemy.exc import IntegrityError, DataError

from .normalize_data import normalize_data, generalize_samples

def extract_table(csv_data):
    tbl = csv_data
    if tbl is None:
        return
    f = StringIO()
    f.write(tbl.decode())
    f.seek(0)
    df = read_csv(f)
    df = df.iloc[:,1:]
    return normalize_data(df)

def infer_project_name(fp):
    folders = fp.split("/")[:-1]
    return max(folders, key=len)

class LaserchronImporter(BaseImporter):
    """
    A basic Sparrow importer for cleaned ETAgeCalc and NUPM AgeCalc files.
    """
    authority = "ALC"

    def import_all(self):
        q = self.db.session.query(self.db.model.data_file)
        self.iteritems(q)

    def import_datafile(self, rec):
        """
        data file -> sample(s)
        """
        if "NUPM-MON" in rec.basename:
            raise SparrowImportError("NUPM-MON files are not handled yet")
        if not rec.csv_data:
            raise SparrowImportError("CSV data not extracted")
        data, meta = extract_table(rec.csv_data)
        self.meta = meta
        data.index.name = 'analysis'

        # Start inferring things
        project = infer_project_name(rec.file_path)

        data = generalize_samples(data)

        #data.index = ax.index
        ids = list(data.index.unique(level=0))

        for sample_id in ids:
            print(sample_id)
            df = data.xs(sample_id, level='sample_id', drop_level=False)
            try:
                session = self.import_session(rec, df)
            except DataError as err:
                raise SparrowImportError("Data error")
            except IntegrityError as err:
                raise SparrowImportError("Integrity error")
            return True


    def import_session(self, rec, df):

        date = rec.file_mtime or datetime.min()

        sample_id = df.index.unique(level=0)[0]
        sample = self.sample(id=sample_id)
        session = self.models.session(date=date)
        session._sample = sample
        # Add this to our data file model
        dt = self.db.get_or_create(self.db.model.data_file_type)
        dt._session = session
        dt._sample = sample
        dt._data_file = rec

        self.db.session.add(sample)
        self.db.session.add(session)
        self.db.session.add(dt)

        for i, row in df.iterrows():
            analysis = self.import_analysis(row)
            analysis._session = session
            self.db.session.add(analysis)

    def import_analysis(self, row):
        """
        row -> analysis
        """

        analysis = self.models.analysis(
            session_index=row.name[1],
            analysis_name=row['analysis'])

        analysis.datum_collection = list(self.import_data(row))
        return analysis

    def import_data(self, row):
        for i in row.iteritems():
            d = self.import_datum(*i, row)
            if d is None: continue
            yield d

    def import_datum(self, key, value, row):
        """
        ValueModel -> datum
        """
        if key == 'analysis':
            return None
        if key.endswith("_error"):
            return None
        value = float(value)
        if isnan(value):
            return None

        m = self.meta[key]
        parameter = m.name

        unit = self.unit(m.at['Unit']).id

        err = None
        err_unit = None
        try:
            err_ix = key+"_error"
            err = row.at[err_ix]
            err_unit = self.unit(self.meta[err_ix].at['Unit']).id
        except KeyError:
            pass

        return self.datum(parameter, value,
            unit=unit,
            error=err,
            error_unit=err_unit,
            error_metric="2s")
