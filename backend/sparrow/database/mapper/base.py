from sqlalchemy.ext.automap import automap_base
from ...interface.util import primary_key


class ModelHelperMixins(object):
    """
    Standard mixins for database models
    """

    @classmethod
    def get_or_create(cls, **kwargs):
        defaults = kwargs.pop("defaults", None)
        return cls.db.get_or_create(cls, defaults=defaults, **kwargs)

    def to_dict(self):
        res = {}
        for k, v in self.__table__.c.items():
            res[k] = getattr(self, k)
        return res

    def __repr__(self):
        fmt = lambda v: "–" if v is None else v
        vals = [f"{k}: {fmt(v)}" for k, v in primary_key(self).items()]
        pk_ = ", ".join(vals)
        return f"{self.__class__.__name__}({pk_})"


BaseModel = automap_base(cls=ModelHelperMixins)