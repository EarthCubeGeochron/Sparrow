from .util import primary_key


class ModelHelperMixins:
    """
    Standard mixins for database models
    """

    loaded_from_cache = False

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

    # def _schema(self, *args, **kwargs):
    #     session = kwargs.pop("sqla_session", None)
    #     return model_interface(self, session=session)(*args, **kwargs)
