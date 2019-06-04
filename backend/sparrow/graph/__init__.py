import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

class Query(graphene.ObjectType):
    node = relay.Node.Field()

schema = graphene.Schema(query=Query)
