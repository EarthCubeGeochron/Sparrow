from marshmallow.fields import Nested
from marshmallow.exceptions import RegistryError
from click import echo, secho, style
from shutil import get_terminal_size


def styled_key(k, **kwargs):
    return style("• ", dim=True) + style(k, **kwargs)


sep = "…"
indent = 3


class ModelPrinter(object):
    def __init__(self, nest_level=0):
        self.nest_level = nest_level
        self.width, _ = get_terminal_size()

    def print_nested(self, k, field, level=0):
        prefix = level * indent * " "
        try:
            if level < self.nest_level:
                self.print_model(
                    field.schema, level=level + 1, key=k, exclude=field.exclude
                )
            else:
                self.print_field(
                    k, field.schema, bold=True, level=level, required=field.required
                )
        except (ValueError, RegistryError, AttributeError) as err:
            echo(prefix + styled_key(k) + "  " + style(str(err), fg="red"))

    def print_field(self, key, field, level=0, **kwargs):
        prefix = level * indent * " "
        classname = field.__class__.__name__

        required = getattr(field, "required", kwargs.pop("required", False))

        many_to_one = getattr(field, "many", False)

        row = build_row_styles(
            key,
            classname,
            prefix=prefix,
            level=level,
            width=self.width,
            dump_only=field.dump_only,
            required=required,
            many_to_one=many_to_one,
            **kwargs
        )

        echo(row)

    def __sort_fields(self, a):
        return isinstance(a[1], Nested)

    def print_model(self, model, key=None, level=0, exclude=[], model_alias=None):
        prefix = level * indent * " "

        new_prefix = prefix[0 : len(prefix) - indent]
        if key is not None:
            self.print_field(key, model, level=level - 1, bold=True)
        else:
            model_name = new_prefix + style(model.__class__.__name__, bold=True)
            echo(model_name, nl=False)
            if model_alias is not None:
                echo(style(" / ", dim=True) + str(model_alias))
            else:
                echo()

        fields = list(model.declared_fields.items())
        fields.sort(key=self.__sort_fields)

        for k, v in fields:
            name = v.data_key or k
            if k in exclude:
                continue
            if isinstance(v, Nested):
                self.print_nested(name, v, level=level)
            else:
                self.print_field(name, v, level=level)
        if len(exclude):
            excluded_names = [model.declared_fields[k].data_key or k for k in exclude]
            secho(prefix + "  excluded: " + " ".join(excluded_names), dim=True)

    def __call__(self, model, model_alias=None):
        self.print_model(model, model_alias=model_alias)


def pretty_print(model, nested=0, model_alias=None):
    printer = ModelPrinter(nest_level=nested)
    printer(model, model_alias=model_alias)


def build_row_styles(
    key,
    classname,
    prefix="",
    level=0,
    width=80,
    dump_only=False,
    required=False,
    many_to_one=False,
    **kwargs
):
    modifier = ""
    if many_to_one:
        modifier = "..."

    nfill = width - 4 - level * indent - len(key) - len(classname) - len(modifier)
    dim = dump_only

    return "".join(
        [
            prefix,
            styled_key(key, dim=dim, underline=required),
            style(modifier, dim=dim, bold=True),
            " ",
            style(sep * nfill, dim=True),
            " ",
            style(classname, fg="cyan", dim=True, **kwargs),
        ]
    )


def print_field(*args, **kwargs):
    kwargs["width"] = 40
    kwargs["prefix"] = 2 * indent * " "
    row = build_row_styles(*args, **kwargs)
    echo(row)


def print_key():
    nfill = 40 - 13
    echo(2 * indent * " " + style("Key") + " " * nfill + style("Model type", dim=True))
    print_field("required", "String", required=True)
    print_field("optional", "Integer", required=False)
    print_field("nested", "AnotherModel", required=False, bold=True)
    print_field(
        "many-to-one", "AnotherModel", required=False, bold=True, many_to_one=True
    )
    print_field("dump-only", "String", required=False, dump_only=True)
