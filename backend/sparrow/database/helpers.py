class JointModelCollection(object):
    def __init__(self, *collections):
        self.collections = collections

    def __getattr__(self, name):
        for coll in self.collections:
            try:
                return coll[name]
            except KeyError:
                continue
        raise KeyError(name)

    def __iter__(self):
        for coll in self.collections:
            for model in coll:
                yield model

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
