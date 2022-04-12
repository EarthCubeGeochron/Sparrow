def primary_key(instance):
    """Get primary key properties for a SQLAlchemy model.
    :param model: SQLAlchemy model class
    """
    mapper = instance.__class__.__mapper__
    prop_list = [mapper.get_property_by_column(column) for column in mapper.primary_key]
    return {prop.key: getattr(instance, prop.key) for prop in prop_list}

def classname_for_table(table):
    if table.schema is not None:
        return f"{table.schema}_{table.name}"
    return table.name


def _classname_for_table(cls, table_name, table):
    # We have to be fancy for SQLAlchemy
    return classname_for_table(table)


def trim_postfix(target, postfix="_id"):
    if target.endswith(postfix):
        return target[: -len(postfix)]
    return target


# For automapping
def name_for_scalar_relationship(base, local_cls, referred_cls, constraint):
    base_name = referred_cls.__table__.name.lower()
    # Use name of column if we have a simple relationship
    # with one local column not named 'id' (we could probably
    # use 'not a FK' and it would be better)
    # if len(constraint.column_keys) == 1:
    #     n = constraint.column_keys[0]
    #     if n != 'id':
    #         base_name = trim_postfix(n)

    return "_" + base_name


def name_for_collection_relationship(base, local_cls, referred_cls, constraint):
    # if referred_cls.__table__.name == 'datum_type' and local_cls.__table__.name == 'unit':
    cls_name = referred_cls.__name__.lower()
    # Collection creation override for self-referential relationships.
    # We could probably generalize this for all 'through' models
    # if referred_cls.__table__.name in ["parameter", "material"]:
    #    cls_name += "_" + "_".join(col.name for col in constraint.columns)
    return cls_name + "_collection"


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
