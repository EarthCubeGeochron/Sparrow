# TODO: watch for merge of PR #164 on graphene-sqlalchemy, and then
# import this code from there.
from functools import partial
from promise import is_thenable, Promise
from sqlalchemy.orm.query import Query

from graphene.relay import Connection, ConnectionField
from graphene.relay.connection import PageInfo
from graphql_relay.connection.arrayconnection import connection_from_list_slice
from graphene_sqlalchemy import SQLAlchemyConnectionField
from flask_jwt_extended import jwt_optional

from .filters import filter_class_for_module, Filter


class FilterableConnectionField(SQLAlchemyConnectionField):
    def __init__(self, type, *args, **kwargs):
        if "filter" not in kwargs and issubclass(type, Connection):
            model = type.Edge.node._type._meta.model
            kwargs.setdefault("filter", filter_class_for_module(model))
        elif "filter" in kwargs and kwargs["filter"] is None:
            del kwargs["filter"]
        super(FilterableConnectionField, self).__init__(type, *args, **kwargs)

    # For now, we require logged-in state to use ANY graphql API functions.
    # This could change for compatibility with the REST API.
    @classmethod
    @jwt_optional
    def get_query(cls, model, info, filter=None, **kwargs):
        query = super(FilterableConnectionField, cls).get_query(model, info, **kwargs)
        if filter:
            for k, v in filter.items():
                query = Filter.add_filter_to_query(query, model, k, v)
        return query
