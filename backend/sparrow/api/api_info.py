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


def get_field_description(type_: str, field_name: str, schema):

    schema_name = schema.opts.model.__name__.lower()

    field_descriptions = api_help["fields"]["descriptions"]
    if "schema" in type_.lower():
        description = f"An unique ID specifying a {field_name} or a JSON object in structure with the {type_}"
        if "[]" in type_.lower():
            description = f"A list of unique IDs specifying {field_name}s or a JSON object with the schema structure matching {type_}"
    else:
        description = field_descriptions.get(type_.lower(), f"A {type_} describing ")
        description += field_name

    if schema_name in field_descriptions:
        description = field_descriptions[schema_name].get(field_name, description)

    return {"description": description}


def get_field_json_values(type_: str, name: str, schema):
    """get the values api_help['fields']"""
    if type_.lower() == "uuid":
        return ""
        
    schema_name = schema.opts.model.__name__.lower()
    json_values = api_help["fields"]["json-values"]

    if "schema" in type_.lower():
        default_value = json_values["related"]
        if "[]" in type_.lower():
            default_value = json_values["related-list"]

    else:
        default_value = json_values[type_.lower()]

    ## check if schema_name is in api_help
    if schema_name in json_values:
        schema_json = json_values[schema_name]
        default_value = schema_json.get(name, default_value)
    return default_value
