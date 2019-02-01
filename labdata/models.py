"""
In general, Python models are automatically mapped to database objects
in order to have a 'single source of truth' for the database schema.
However, some models used in application logic have tightly coupled
code that is closely tied to the specific database representation.
Declarative models for these objects are defined here.
"""
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, String
from passlib.hash import pbkdf2_sha256 as sha256

Base = automap_base()

class User(Base):
    __tablename__ = "user"
    # Columns are automagically mapped
    # *NEVER* directly set the password column.
    def set_password(self, plaintext):
        self.password = sha256.hash(plaintext)
    def is_correct_password(self, plaintext):
        return sha256.verify(self.password, plaintext)

