from sqlalchemy.ext.automap import automap_base

class ModelHelperMixins(object):
    """
    Standard mixins for database models
    """
    @classmethod
    def get_or_create(cls, **kwargs):
        defaults = kwargs.pop('defaults', None)
        return cls.db.get_or_create(cls, defaults=defaults, **kwargs)

    def to_dict(self):
        res = {}
        for k,v in self.__table__.c.items():
            res[k] = getattr(self, k)
        return res

BaseModel = automap_base(cls=ModelHelperMixins)
