"""Where pipeline records meet the database."""

from os import environ
from pathlib import Path

from sparrow.logs import get_logger
from sparrow.pipelines import SourceFile, TopLevelRecord

log = get_logger(__name__)

# The models a data file can be recorded as the source of
_linked_models = {"session": "_session", "sample": "_sample"}


class DatabaseSink:
    """Loads records into a Sparrow database, and keeps track of the files
    they came from so that an unchanged file is not read twice."""

    def __init__(self, db, basedir=None):
        self.db = db
        self.basedir = basedir or environ.get("SPARROW_DATA_DIR")

    def _reference_path(self, source: SourceFile) -> str:
        path = Path(source.path)
        if self.basedir is not None and path.is_relative_to(self.basedir):
            path = path.relative_to(self.basedir)
        return str(path)

    def _data_file(self, source: SourceFile):
        """The record of a file, created or brought up to date."""
        db = self.db
        DataFile = db.model.data_file
        file_path = self._reference_path(source)
        rec = db.session.get(DataFile, source.file_hash)
        if rec is None:
            # New contents at a known path: the earlier version's record, and
            # its links to what was loaded from it, no longer describe the file
            db.session.query(DataFile).filter_by(file_path=file_path).delete()
            rec = DataFile(file_hash=source.file_hash)
        rec.file_path = file_path
        rec.basename = Path(source.path).name
        rec.file_mtime = source.mtime.replace(tzinfo=None)
        rec.source_url = source.source_url
        if source.file_type is not None:
            file_type = db.get_or_create(db.model.data_file_type, id=source.file_type)
            db.session.add(file_type)
            db.session.flush()
            rec.type_id = source.file_type
        db.session.add(rec)
        db.session.commit()
        return rec

    def begin(self, source: SourceFile, *, redo: bool = False) -> bool:
        rec = self._data_file(source)
        if redo:
            return True
        Link = self.db.model.data_file_link
        n_loaded = (
            self.db.session.query(Link)
            .filter_by(file_hash=rec.file_hash)
            .filter(Link.error.is_(None))
            .count()
        )
        return n_loaded == 0

    def load(self, source: SourceFile, records: list[TopLevelRecord]) -> None:
        db = self.db
        rec = self._data_file(source)
        for record in records:
            model = db.load_data(record.model_name, record.to_import_data())
            # Other records are noted without a link, so the file counts as loaded
            key = _linked_models.get(record.model_name)
            linked = {key: model} if key is not None else {}
            link = db.get_or_create(db.model.data_file_link, _data_file=rec, **linked)
            db.session.add(link)
        db.session.commit()

    def fail(self, source: SourceFile, error: Exception) -> None:
        db = self.db
        db.session.rollback()
        log.error(f"{source.path}: {error}")
        rec = self._data_file(source)
        link = db.get_or_create(
            db.model.data_file_link, _data_file=rec, defaults=dict(error=str(error))
        )
        db.session.add(link)
        db.session.commit()
