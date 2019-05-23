from itertools import chain
from sparrow.import_helpers import BaseImporter, SparrowImportError
from datetime import datetime
from io import StringIO
from pandas import read_csv, concat
from math import isnan
import numpy as N
from click import secho
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

    def import_all(self, redo=False):
        self.redo = redo
        q = self.db.session.query(self.db.model.data_file)
        self.iter_records(q, redo=redo)

    def import_one(self, basename):
        q = (self.db.session.query(self.db.model.data_file)
                .filter_by(basename=basename))
        self.iter_records(q, redo=True)

    def import_datafile(self, fn, rec, redo=False):
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

        data = generalize_samples(data)

        ids = list(data.index.unique(level=0))

        for sample_id in ids:
            df = data.xs(sample_id, level='sample_id', drop_level=False)
            try:
                yield self.import_session(rec, df)
            except IntegrityError as err:
                raise SparrowImportError(str(err.orig))

    def import_session(self, rec, df):

        # Infer project name
        project_name = infer_project_name(rec.file_path)
        project = self.project(project_name)

        date = rec.file_mtime or datetime.min()

        sample_id = df.index.unique(level=0)[0]
        sample = self.sample(name=sample_id)
        self.db.session.add(project)
        self.db.session.add(sample)

        session = self.db.get_or_create(
            self.m.session,
            date=date,
            project_id=project.id,
            sample_id=sample.id)

        self.db.session.flush()

        dup = df['analysis'].duplicated(keep='first')
        if dup.astype(bool).sum() > 0:
            self.warn(f"Duplicate analyses found for sample {sample_id}")
        df = df[~dup]

        for i, row in df.iterrows():
            list(self.import_analysis(row, session))

        return session

    def import_analysis(self, row, session):
        """
        row -> analysis
        """
        # session index should not be nan
        try:
            ix = int(row.name[1])
        except ValueError:
            ix = None

        analysis = self.add_analysis(
            session,
            session_index=ix,
            analysis_name=str(row['analysis']))

        for i in row.iteritems():
            d = self.import_datum(analysis, *i, row)
            if d is None: continue
            yield d

    def import_datum(self, analysis, key, value, row):
        """
        Each value in a table row -> datum
        """
        if key == 'analysis':
            return None
        if key.endswith("_error"):
            return None
        if key == 'best_age':
            # We test for best ages separately, since they
            # must be one of the other ages
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
            i = self.meta[err_ix].at['Unit']
            err_unit = self.unit(i).id
        except KeyError:
            pass

        is_age = key.startswith("age_")

        datum = self.datum(analysis, parameter, value,
            unit=unit,
            error=err,
            error_unit=err_unit,
            error_metric="2s",
            is_interpreted=is_age)

        if is_age:
            # Test if it is a "best age"
            best_age = float(row.at['best_age'])
            datum.is_accepted = N.allclose(value, best_age)
        return datum
