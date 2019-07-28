import graphene
from graphene import String, Field
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from .filterable_query import FilterableConnectionField

# https://github.com/alexisrolland/flask-graphene-sqlalchemy/wiki/Flask-Graphene-SQLAlchemy-Tutorial

connection_fields = dict()

def connection(model_type):
    class_name = model_type.__name__+"Connection"
    cls = connection_fields.get(class_name, None)
    if not cls:
        class Meta:
            node = model_type
        # Create a class dynamically
        cls = type(class_name, (relay.Connection,), {"Meta": Meta})
        connection_fields[class_name] = cls
    return FilterableConnectionField(cls)

def connection_field_factory(relationship, registry, **field_kwargs):
    # https://github.com/graphql-python/graphene-sqlalchemy/blob/master/graphene_sqlalchemy/fields.py
    model = relationship.mapper.entity
    model_type = registry.get_type_for_model(model)
    return connection(model_type)

def build_schema(db):

    class Datum(SQLAlchemyObjectType):
        class Meta:
            model = db.model.datum
            model.db_id = model.id
            interfaces = (relay.Node, )
            connection_field_factory = connection_field_factory

    class DatumType(SQLAlchemyObjectType):
        class Meta:
            model = db.model.datum_type
            model.db_id = model.id
            interfaces = (relay.Node,)
            connection_field_factory = connection_field_factory

    class Analysis(SQLAlchemyObjectType):
        class Meta:
            model = db.model.analysis
            model.db_id = model.id
            interfaces = (relay.Node,)
            connection_field_factory = connection_field_factory

    class Query(graphene.ObjectType):
        node = relay.Node.Field()
        datum = connection(Datum)
        datum_type = connection(DatumType)
        analysis = connection(Analysis)

    return graphene.Schema(query=Query, types=[Datum, DatumType, Analysis])
