from marshmallow_sqlalchemy import ModelSchema, exceptions
from marshmallow_sqlalchemy.fields import Related
from marshmallow.fields import Nested
from marshmallow.exceptions import RegistryError
from click import echo, secho, style
from textwrap import indent


def styled_key(k):
    return style("• ", dim=True)+k


sep = "…"
indent = 3

class ModelPrinter(object):
    def __init__(self, nest_level=0):
        self.nest_level = nest_level

    def print_nested(self, k, field, level=0):
        prefix = level*indent*" "
        if level < self.nest_level:
            try:
                self.print_model(field.schema, level=level+1, key=k)
            except ValueError as err:
                echo(field.schema.exclude)
                echo(prefix+styled_key(k)+style(str(err), fg="red"))
            except RegistryError:
                # Ignore nested fields that aren't
                pass
            except AttributeError as err:
                echo(prefix+styled_key(k)+style(str(err), fg="red"))
        else:
            self.print_field(k, field.schema, bold=True, level=level)
            #echo(prefix+styled_key(k)+style(": ", dim=True)+style(field.schema.__class__.__name__, bold=True))


    def print_field(self, key, field, level=0, **kwargs):
        prefix = level*indent*" "
        classname = field.__class__.__name__
        nfill = 60-level*indent-len(key)-len(classname)

        row = "".join([
            prefix,
            styled_key(key),
            " ",
            style(sep*nfill, dim=True),
            " ",
            style(classname, fg="cyan", dim=True, **kwargs)
        ])
        echo(row)

    def __sort_fields(self, a):
        return isinstance(a[1],Nested)

    def print_model(self, model, key=None, level=0):
        prefix = level*indent*" "

        new_prefix = prefix[0:len(prefix)-indent]
        if key is not None:
            self.print_field(key, model, level=level-1, bold=True)
            #new_prefix += styled_key(key)+style(": ", dim=True)
        else:
            echo(new_prefix+style(model.__class__.__name__, bold=True))

        fields = list(model._declared_fields.items())
        fields.sort(key=self.__sort_fields)

        for k, v in fields:
            if isinstance(v, Nested):
                self.print_nested(k, v, level=level)
            else:
                self.print_field(k, v, level=level)

    def __call__(self, model):
        self.print_model(model)


def pretty_print(model, nested=0):
    printer = ModelPrinter(nest_level=nested)
    printer(model)
