from flask_restful import Api

class APIResourceCollection(object):
    """
    An extension to the `flask_restful` API that allows quick
    creation of nested API routes.
    """
    def __init__(self):
        self.resource_arguments = []

    def add_resource(self, *args, **kwargs):
        self.resource_arguments.append((args, kwargs))

    # Decorator function for nested API resource
    def resource(self, *endpoints, **kw):
        def func(cls):
            self.add_resource(cls, *endpoints, **kw)
        return func

class API(Api):
    def add_resource(self, resource, *endpoints, **kw):
        try:
            super().add_resource(resource, *endpoints, **kw)
        except AttributeError:
            if len(endpoints) != 1:
                raise IndexError("A single endpoint must be specified for "
                                 "API resource collections.")
            endpoint, = endpoints

            for (args,kwargs) in resource.resource_arguments:
                (r, e) = args
                e = endpoint + e
                super().add_resource(r, e, **kwargs)
