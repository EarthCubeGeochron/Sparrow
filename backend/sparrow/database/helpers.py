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
    def __init__(self, base, overrides):
        self.automap_base = base
        self.base_classes = base.classes
        self.__overrides = {}

    @property
    def __not_overridden(self):
        return {k:c for k,c
                in self.base_classes.items()
                if k not in self.__overrides}

    def register(self, *classes):
        for cls in classes:
            k = classname_for_table(cls.__table__)
            self.__overrides[k] = cls

    def __getattr__(self, name):
        if name in self.__overrides:
            return self.__overrides[name]
        return getattr(self.base_classes, name)

    def __len__(self):
        return len(self.__overrides)+len(self.__not_overridden)

    def __iter__(self):
        yield from self.__not_overridden
        yield from self.__overrides

    def keys(self):
        return list(chain(
            self.__not_overridden.keys(),
            self.__overrides.keys()))

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
