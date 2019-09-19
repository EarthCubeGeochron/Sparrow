from sqlalchemy.sql import ClauseElement
from itertools import chain

def classname_for_table(table):
    if table.schema is not None:
        return f"{table.schema}_{table.name}"
    return table.name

def _classname_for_table(cls, table_name, table):
    # We have to be fancy for SQLAlchemy
    return classname_for_table(table)

def get_or_create(session, model, defaults=None, **kwargs):
    """
    Get an instance of a model, or create it if it doesn't
    exist.

    https://stackoverflow.com/questions/2546207
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        instance._created = False
        return instance
    else:
        params = dict((k, v) for k, v in kwargs.items()
            if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        instance._created = True
        return instance

class ModelCollection(object):
    def __init__(self, models=None):
        self.__models = {}
        if models is None:
            return
        self.register(*models)

    def register(self, *classes):
        for cls in classes:
            k = classname_for_table(cls.__table__)
            self.__models[k] = cls

    def __getattr__(self, name):
        try:
            return self.__models[name]
        except KeyError:
            raise AttributeError(name)

    def __len__(self):
        return len(self.__models)

    def __iter__(self):
        yield from self.__models

    def keys(self):
        return [k for k in self.__models.keys()]

class TableCollection(object):
    """
    Table collection object that returns automapped tables
    """
    def __init__(self, models):
        self.models = models
    def __getattr__(self, name):
        return getattr(self.models, name).__table__
    def __iter__(self):
        for model in self.models:
            yield model.__table__
