import graphene
from graphene import String, Field
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from graphene_sqlalchemy.utils import to_type_name
from .filterable_query import FilterableConnectionField
from sqlalchemy.types import INTEGER
from sparrow import get_logger

log = get_logger(__name__)

# https://github.com/alexisrolland/flask-graphene-sqlalchemy/wiki/Flask-Graphene-SQLAlchemy-Tutorial
# https://github.com/flavors/django-graphql-jwt/issues/6
# https://github.com/graphql-python/graphene-sqlalchemy/blob/master/examples/flask_sqlalchemy/schema.py

connection_fields = dict()

def connection(model_type):
    class_name = to_type_name(model_type.__name__+"_connection")
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

def resolve_primary_key(self, info):
    """
    This is basically the same as the default ID resolver
    """
    keys = self.__mapper__.primary_key_from_instance(self)
    return tuple(keys) if len(keys) > 1 else keys[0]

def is_integer(v):
    return issubclass(INTEGER, type(v))

class DatabaseIntegerID(graphene.Interface):
    primary_key = graphene.Int()

class DatabaseStringID(graphene.Interface):
    primary_key = graphene.String()

def primary_key_interface(model):
    v = model.__mapper__.primary_key
    if len(v) > 1:
        return []
    # We only provide a primary key item if there is a *single*
    # primary key. We may implement multikey if we need it
    if is_integer(v[0].type):
        return (DatabaseIntegerID,)
    else:
        return (DatabaseStringID,)

def graphql_object_factory(_model, id_param=None):
    """
    ID Resolution: [https://github.com/graphql-python/graphene-sqlalchemy/blob/89c37265012b0e296147a1631b44d8f5d943dc59/graphene_sqlalchemy/types.py#L312]
    This is a straightforward reimplementation the default id
    resolver for SQLAlchemy objects in Graphene-SQLAlchemy.

    GraphQL IDs are represented as Base64-encodings of the format
    <model_name>:<primary_key> for single-key values.
    """

    name_ = to_type_name(_model.__name__)

    class Meta:
        model = _model
        interfaces = (relay.Node, *primary_key_interface(model))
        connection_field_factory = connection_field_factory
        name = name_

    return type(name_, (SQLAlchemyObjectType,), dict(
        Meta=Meta,
        resolve_primary_key=resolve_primary_key))

def build_schema(db):
    types = []
    fields = dict(
        node = relay.Node.Field())
    for model in db.automap_base.classes:
        log.debug(f"Building GraphQL schema for {model.__name__}")
        obj = graphql_object_factory(model)
        types.append(obj)
        fields[model.__name__] = connection(obj)

    Query = type("Query", (graphene.ObjectType,), fields)

    return graphene.Schema(query=Query, types=types)
