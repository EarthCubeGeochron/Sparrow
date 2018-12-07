from flask import Flask, Blueprint
from flask_restful import Resource, Api, reqparse
from sqlalchemy.schema import Table
from sqlalchemy import MetaData

# eventually should use **Marshmallow** or similar
# for parsing incoming API requests

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

        def infer_primary_key():
            pk = table.primary_key
            if len(pk) == 1:
                return list(pk)[0]
            # Check PK column a few possible ways
            primary_key = kwargs.pop("primary_key", None)
            if primary_key is not None:
                return table.c[primary_key]
            for i in ('id', tablename+'_id'):
                pk = table.c.get(i, None)
                if pk is not None: return pk
            return list(table.c)[0]

        key = infer_primary_key()

        parser = reqparse.RequestParser()
        parser.add_argument('offset', type=int, help='Query offset', default=0)
        parser.add_argument('limit', type=int, help='Query limit', default=100)


        class TableModel(Resource):
            def get(self):
                args = parser.parse_args()

                return (db.session.query(table)
                          .offset(args['offset'])
                          .limit(args['limit'])
                          .all())

        class RecordModel(Resource):
            def get(self, id):
                return (db.session.query(table)
                    .filter(key==id)
                    .first())


        # Dynamically change class name,
        # this kind of metaprogrammy wizardry
        # may cause problems later
        TableModel.__name__ = tablename
        RecordModel.__name__ = tablename+'_record'

        route = f"/{tablename}"
        self.add_resource(TableModel, route)

        tname = key.type.python_type.__name__
        if tname != 'int':
            tname = 'string'
        self.add_resource(RecordModel, f"{route}/<{tname}:id>")
