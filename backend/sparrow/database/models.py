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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column
from os import environ
from sqlalchemy.orm import relationship
from uuid import uuid4
from .mapper import BaseModel


class User(BaseModel):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

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
    __tablename__ = "project"
    __table_args__ = {'extend_existing': True}

    def add_researcher(self, researcher):
        self.researcher_collection.append(researcher)

    def add_session(self, session):
        self.session_collection.append(session)

class Session(BaseModel):
    __tablename__ = "session"
    __table_args__ = {'extend_existing': True}
    # Define UUID column so it is caught as unique
    uuid = Column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid4,
        server_default="uuid_generate_v4()",
    )
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
    __tablename__ = "datum_type"
    __table_args__ = {'extend_existing': True}

    # We need to override foreign keys
    _error_unit = relationship("vocabulary_unit", foreign_keys="DatumType.error_unit")
    _unit = relationship("vocabulary_unit", foreign_keys="DatumType.unit")
