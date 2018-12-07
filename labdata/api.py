from flask import Flask, Blueprint
from flask_restful import Resource, Api
from sqlalchemy.schema import Table
from sqlalchemy import MetaData

class APIv1(Api):
    """
    Version 1 API for Lab Data Interface

    Includes functionality for autogenerating routes
    from database tables and views.
    """
    def __init__(self, database):
        self.db = database
        self.blueprint = Blueprint('api', __name__)
        super().__init__(self.blueprint)

    def build_route(self, tablename, **kwargs):
        db = self.db
        schema = kwargs.pop("schema", "public")
        meta = MetaData(schema=schema)
        table = Table(tablename, meta,
            autoload=True, autoload_with=db.engine, **kwargs)
        q = db.session.query(table)

        class TableModel(Resource):
            def get(self):
                return q.limit(1000).all()

        # Dynamically change class name,
        # this kind of metaprogrammy wizardry
        # may cause problems later
        TableModel.__name__ = tablename

        self.add_resource(TableModel, '/'+tablename)
