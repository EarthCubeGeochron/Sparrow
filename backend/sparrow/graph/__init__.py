import graphene
from graphene import String
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

def build_schema(db):

    class Datum(SQLAlchemyObjectType):
        class Meta:
            model = db.model.datum
            interfaces = (relay.Node,)

    class DatumConnection(relay.Connection):
        class Meta:
            node = Datum

    class Query(graphene.ObjectType):
        node = relay.Node.Field()
        data = SQLAlchemyConnectionField(DatumConnection)

    return graphene.Schema(query=Query)
