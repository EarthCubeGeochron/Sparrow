

def classname_for_table(table):
    if table.schema is not None:
        return f"{table.schema}_{table.name}"
    return table.name


def _classname_for_table(cls, table_name, table):
    # We have to be fancy for SQLAlchemy
    return classname_for_table(table)


# For automapping
def name_for_scalar_relationship(base, local_cls, referred_cls, constraint):
    return "_"+referred_cls.__table__.name.lower()


class BaseCollection(object):
    def __repr__(self):
        keys = ",\n  ".join(self.keys())
        return f"{self.__class__.__name__}: [\n  {keys}\n]"


class ModelCollection(BaseCollection):
    def __init__(self, models=None):
        self.__models = {}
        if models is None:
            return
        self.register(*models)

    def register(self, *classes):
        for cls in classes:
            k = classname_for_table(cls.__table__)
            self.add(k, cls)

    def add(self, key, value):
        self.__models[key] = value

    def __getattr__(self, name):
        try:
            return self.__models[name]
        except KeyError:
            raise AttributeError(name)

    def __len__(self):
        return len(self.__models)

    def __iter__(self):
        yield from self.__models.values()

    def keys(self):
        return [k for k in self.__models.keys()]


class TableCollection(BaseCollection):
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

    def keys(self):
        return self.models.keys()
