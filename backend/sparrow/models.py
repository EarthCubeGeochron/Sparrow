"""
In general, Python models are automatically mapped to database objects
in order to have a 'single source of truth' for the schema.
However, some models used in application logic have code that is
tightly coupled to the specific database representation.
Declarative models for these objects are defined here.
"""
from sqlalchemy.ext.automap import automap_base
from werkzeug.security import generate_password_hash, check_password_hash
from os import environ
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer

from sqlalchemy.ext.declarative import declared_attr

class BaseClass(object):
    pass
    # Shim for future expansion

Base = automap_base(cls=BaseClass)

class User(Base):
    __tablename__ = "user"
    # Columns are automagically mapped from database
    # *NEVER* directly set the password column.
    def set_password(self, plaintext):
        # 'salt' the passwords to prevent brute forcing
        salt = environ.get("SPARROW_SECRET_KEY")
        self.password = generate_password_hash(salt+str(plaintext))
    def is_correct_password(self, plaintext):
        salt = environ.get("SPARROW_SECRET_KEY")
        return check_password_hash(self.password, salt+str(plaintext))

class Project(Base):
    __tablename__ = "project"
    def add_researcher(self, researcher):
        self.researcher_collection.append(researcher)

    def add_session(self, session):
        self.session_collection.append(session)

class Session(Base):
    __tablename__ = "session"
    def get_attribute(self, type):
        pass
