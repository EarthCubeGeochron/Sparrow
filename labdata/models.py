"""
In general, Python models are automatically mapped to database objects
in order to have a 'single source of truth' for the schema.
However, some models used in application logic have code that is
tightly coupled to the specific database representation.
Declarative models for these objects are defined here.
"""
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, String
from werkzeug.security import generate_password_hash, check_password_hash
from os import environ

Base = automap_base()

class User(Base):
    __tablename__ = "user"
    # Columns are automagically mapped
    # *NEVER* directly set the password column.
    def set_password(self, plaintext):
        # 'salt' the passwords to prevent brute forcing
        salt = environ.get("LABDATA_SECRET_KEY")
        self.password = generate_password_hash(salt+str(plaintext))
    def is_correct_password(self, plaintext):
        salt = environ.get("LABDATA_SECRET_KEY")
        return check_password_hash(self.password, salt+str(plaintext))

