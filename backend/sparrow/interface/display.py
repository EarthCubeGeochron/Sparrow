from marshmallow_sqlalchemy import ModelSchema, exceptions
from marshmallow_sqlalchemy.fields import Related
from marshmallow.fields import Nested
from marshmallow.exceptions import RegistryError
from click import echo, secho, style
from textwrap import indent


def styled_key(k):
    return style("• ", dim=True)+k+style(": ", dim=True)


def to_json_schema(model):
    return json_schema.dump(model)


def pretty_print(model, prefix="", key=None):
    new_prefix = prefix[0:len(prefix)-4]
    if key is not None:
        new_prefix += styled_key(key)
    print(new_prefix+model.__class__.__name__)
    for k, v in model._declared_fields.items():
        if isinstance(v, Nested):
            if len(prefix) < 6:
                try:
                    pretty_print(v.schema, prefix=prefix+"    ", key=k)
                except ValueError as err:
                    echo(v.schema.exclude)
                    echo(prefix+styled_key(k)+style(str(err), fg="red"))
                except RegistryError:
                    # Ignore nested fields that aren't
                    pass
                except AttributeError as err:
                    echo(prefix+styled_key(k)+style(str(err), fg="red"))
        else:
            classname = v.__class__.__name__
            nfill = 32-len(k)-len(classname)

            row = "".join([
                prefix,
                styled_key(k),
                style("."*nfill,dim=True),
                style(classname, fg="cyan", dim=True)
            ])
            echo(row)
