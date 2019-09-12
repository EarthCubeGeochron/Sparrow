import graphene
from graphene import String, Field
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from .filterable_query import FilterableConnectionField
from .util import camelize

# https://github.com/alexisrolland/flask-graphene-sqlalchemy/wiki/Flask-Graphene-SQLAlchemy-Tutorial
# https://github.com/flavors/django-graphql-jwt/issues/6

connection_fields = dict()

def connection(model_type):
    class_name = camelize(model_type.__name__)+"Connection"
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

def graphql_object_factory(_model, id_param=None):
    class Meta:
        model = _model
        interfaces = (relay.Node, )
        connection_field_factory = connection_field_factory
    return type(camelize(_model.__name__), (SQLAlchemyObjectType,), dict(Meta=Meta))

def build_schema(db):
    types = []
    fields = dict(
        node = relay.Node.Field())
    for model in db.automap_base.classes:
        obj = graphql_object_factory(model)
        types.append(obj)
        fields[model.__name__] = connection(obj)

    Query = type("Query", (graphene.ObjectType,), fields)

    return graphene.Schema(query=Query, types=types)
