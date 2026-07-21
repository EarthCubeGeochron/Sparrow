"""
In general, Python models are automatically mapped to database objects
in order to have a 'single source of truth' for the schema.
However, some models used in application logic have code that is
tightly coupled to the specific database representation.
Declarative extensions for these objects are defined here.

TODO: this module bundles convenience methods with core functionality
(e.g. password hashing). These should be decoupled. Also, things used
in the API should be separately handled than things only used in import
scripts.
"""
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey, Table
from geoalchemy2 import Geometry
from os import environ
from sqlalchemy.orm import relationship
from uuid import uuid4
from .mapper import BaseModel


class User(BaseModel):
    if BaseModel.loaded_from_cache:
        __table__ = BaseModel.metadata.tables["user"]
    else:
        __tablename__ = "user"
        __table_args__ = {"extend_existing": True}
        username = Column(String, primary_key=True)
        password = Column(String)
        researcher_id = Column(Integer)

    # Columns are automagically mapped from database
    # *NEVER* directly set the password column.

    def set_password(self, plaintext):
        # 'salt' the passwords to prevent brute forcing
        salt = environ.get("SPARROW_SECRET_KEY")
        self.password = generate_password_hash(salt + str(plaintext))

    def is_correct_password(self, plaintext):
        salt = environ.get("SPARROW_SECRET_KEY")
        return check_password_hash(self.password, salt + str(plaintext))


class Project(BaseModel):
    if BaseModel.loaded_from_cache:
        __table__ = BaseModel.metadata.tables["project"]
    else:
        __tablename__ = "project"
        __table_args__ = {"extend_existing": True}
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)
        description = Column(String)
        embargo_date = Column(DateTime)
        location_name = Column(String)
        location_name_autoset = Column(Boolean)
        location = Column(Geometry)
        location_precision = Column(Integer)

    def add_researcher(self, researcher):
        self.researcher_collection.append(researcher)

    def add_session(self, session):
        self.session_collection.append(session)


class Session(BaseModel):
    if BaseModel.loaded_from_cache:
        __table__ = BaseModel.metadata.tables["session"]
    else:
        __tablename__ = "session"
        __table_args__ = {"extend_existing": True}
        id = Column(Integer, primary_key=True)
        # Define UUID column so it is caught as unique
        uuid = Column(
            "uuid",
            UUID(as_uuid=True),
            unique=True,
            nullable=False,
            server_default="uuid_generate_v4()",
        )
        instrument_session_id = Column(Integer)
        sample_id = Column(Integer)
        project_id = Column(Integer)
        publication_id = Column(Integer)
        date = Column(DateTime, nullable=False)
        end_date = Column(DateTime)
        date_precision = Column(String)
        name = Column(String)
        instrument = Column(Integer)
        technique = Column(String)
        target = Column(String)
        embargo_date = Column(DateTime)
        note = Column(String)
        data = Column(JSONB)

    def get_attribute(self, type):
        # There has got to be a better way to get self!
        att = self.db.model.attribute
        an = self.db.model.analysis
        return (
            self.db.session.query(att)
            .filter(att.parameter == type)
            .join(an.attribute_collection)
            .filter(an.session_id == self.id)
        ).all()


class DatumType(BaseModel):
    if BaseModel.loaded_from_cache:
        __table__ = BaseModel.metadata.tables["datum_type"]
    else:
        __tablename__ = "datum_type"
        __table_args__ = {"extend_existing": True}
        id = Column(Integer, primary_key=True)
        parameter = Column("parameter", String)

        # We need to override foreign keys
        unit = Column("unit", String, ForeignKey("vocabulary.unit.id"))
        error_unit = Column("error_unit", String, ForeignKey("vocabulary.unit.id"))
        error_metric = Column(
            "error_metric", String
        )
        is_computed = Column(Boolean)
        is_interpreted = Column(Boolean)
        description = Column(String)
        _unit = relationship("vocabulary_unit", foreign_keys=[unit])
        _error_unit = relationship(
            "vocabulary_unit", foreign_keys=[error_unit], back_populates=None
        )
