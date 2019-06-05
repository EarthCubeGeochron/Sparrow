import graphene
from graphene import String
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

# https://github.com/alexisrolland/flask-graphene-sqlalchemy/wiki/Flask-Graphene-SQLAlchemy-Tutorial

def build_schema(db):

    class Datum(SQLAlchemyObjectType):
        class Meta:
            model = db.model.datum
            model.db_id = model.id
            interfaces = (relay.Node,)

    class DatumConnection(relay.Connection):
        class Meta:
            node = Datum

    class Query(graphene.ObjectType):
        node = relay.Node.Field()
        datum = relay.Node.Field(Datum)
        data = SQLAlchemyConnectionField(DatumConnection)

    return graphene.Schema(query=Query, types=[Datum])
