from yaml import safe_load
from ..util import relative_path
from ..database.mapper.util import classname_for_table


with open(relative_path(__file__, ".", "api-help.yaml"), "r") as f:
    api_help = safe_load(f)


def model_description(schema):
    name = classname_for_table(schema.opts.model.__table__)
    return api_help["models"].get(
        name, f"An autogenerated route for the '{name}' model"
    )


def model_examples(schema):
    name = classname_for_table(schema.opts.model.__table__)
    return api_help["examples"].get(
        name, [f"An autogenerated example for the '{name}' model"]
    )


def root_example():
    return api_help["root"]["examples"]


def root_info():
    return api_help["root"]["info"]


def meta_info():
    return api_help["meta"]