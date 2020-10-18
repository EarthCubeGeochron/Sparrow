from webargs.fields import DelimitedList, Str, Int


class BaseFilter:
    params = None
    help = None

    def __init__(self, model):
        self.model = model

    def should_apply(self):
        return True

    def apply(self, query, args):
        return query

    def __call__(self, query, args):
        if not self.should_apply():
            return query
        return self.apply(args, query)


class AuthorityFilter(BaseFilter):
    params = dict(authority=Str(missing=None))
    help = dict(authority="Authority")

    def should_apply(self):
        return hasattr(self.model, "authority")

    def apply(self, args, query):
        return query.filter(self.model.authority == args["authority"])
