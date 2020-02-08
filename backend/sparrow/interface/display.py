from marshmallow.fields import Nested
from marshmallow.exceptions import RegistryError
from click import echo, secho, style, get_terminal_size


def styled_key(k, **kwargs):
    return style("• ", dim=True)+style(k, **kwargs)


sep = "…"
indent = 3

class ModelPrinter(object):
    def __init__(self, nest_level=0):
        self.nest_level = nest_level
        self.width, _ = get_terminal_size()

    def print_nested(self, k, field, level=0):
        prefix = level*indent*" "
        if level < self.nest_level:
            try:
                self.print_model(field.schema, level=level+1, key=k,
                                 exclude=field.exclude)
            except (ValueError, RegistryError, AttributeError) as err:
                echo(prefix+styled_key(k)+"  "+style(str(err), fg="red"))
        else:
            self.print_field(k, field.schema, bold=True, level=level, required=field.required)


    def print_field(self, key, field, level=0, **kwargs):
        prefix = level*indent*" "
        classname = field.__class__.__name__

        modifier = ""
        if getattr(field, 'many', False):
            modifier = "..."

        nfill = self.width-4-level*indent-len(key)-len(classname)-len(modifier)

        required = getattr(field, 'required', kwargs.pop('required', False))

        dim = field.dump_only


        row = "".join([
            prefix,
            styled_key(key, dim=dim, underline=required),
            style(modifier, dim=dim, bold=True),
            " ",
            style(sep*nfill, dim=True),
            " ",
            style(classname, fg="cyan", dim=True, **kwargs)
        ])
        echo(row)

    def __sort_fields(self, a):
        return isinstance(a[1], Nested)

    def print_model(self, model, key=None, level=0, exclude=[]):
        prefix = level*indent*" "

        new_prefix = prefix[0:len(prefix)-indent]
        if key is not None:
            self.print_field(key, model, level=level-1, bold=True)
        else:
            echo(new_prefix+style(model.__class__.__name__, bold=True))

        fields = list(model.declared_fields.items())
        fields.sort(key=self.__sort_fields)

        for k, v in fields:
            if k in exclude:
                continue
            if isinstance(v, Nested):
                self.print_nested(k, v, level=level)
            else:
                self.print_field(k, v, level=level)
        if len(exclude):
            secho(prefix+"  excluded: "+" ".join(exclude), dim=True)


    def __call__(self, model):
        self.print_model(model)


def pretty_print(model, nested=0):
    printer = ModelPrinter(nest_level=nested)
    printer(model)
