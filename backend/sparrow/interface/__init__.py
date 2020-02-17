from sparrow.plugins import SparrowCorePlugin
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, ModelSchema, exceptions
from marshmallow_sqlalchemy.fields import Related
from marshmallow.fields import Nested
from marshmallow_jsonschema import JSONSchema
from marshmallow_sqlalchemy.fields import get_primary_keys, ensure_list
from marshmallow.fields import Field, Raw
from marshmallow.decorators import pre_load, post_load
from sqlalchemy.exc import StatementError
from click import secho

from .converter import SparrowConverter, to_schema_name
from ..database.mapper.util import ModelCollection, classname_for_table


def _jsonschema_type_mapping(self):
    """TODO: this is just a shim"""
    return {'type': 'integer'}


Related._jsonschema_type_mapping = _jsonschema_type_mapping
Nested._jsonschema_type_mapping = _jsonschema_type_mapping

json_schema = JSONSchema()


class BaseMeta:
    model_converter = SparrowConverter
    # Needed for SQLAlchemyAutoSchema
    include_relationships = True
    load_instance = True

def column_is_required(col):
    has_default = (col.server_default is not None) or (col.default is not None)
    return not (col.nullable or has_default)

# def prop_is_required(prop):
#     cols =

def columns_for_prop(prop):
    try:
        return getattr(prop, 'columns')
    except AttributeError:
        return list(getattr(prop, 'local_columns'))


class BaseSchema(SQLAlchemyAutoSchema):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     nested = [k for k,v in self.fields.items() if isinstance(v, Nested)]
    #     self._simple = None
    #     if len(nested) > 0:
    #         self._simple = self.__class__(exclude=nested, partial=True)

    def get_instance(self, data):
        """Gets pre-existing instances if they are available."""
        if self.transient:
            return None

        # Filter on properties that actually have a local column
        filters = {}
        for prop in self.opts.model.__mapper__.iterate_properties:
            val = data.get(prop.key, None)
            if getattr(prop, 'uselist', False):
                continue
            if val is not None:
                filters[prop.key] = val
            else:
                # Required column is unset
                cols = columns_for_prop(prop)
                if hasattr(prop, 'direction'):
                    filters[prop.key] = None

                is_required = any([column_is_required(i) for i in cols])

                if is_required:
                    if len(cols[0].foreign_keys) > 0:
                        # Foreign keys are resolved later
                        # filters[prop.key] = None
                        print(prop)
                        continue
                    # if self.opts.model.__table__.name == 'datum_type':
                    #     import pdb; pdb.set_trace()
                    return super().get_instance(data)
        #if self.opts.model.__table__.name == 'datum':
        #    import pdb; pdb.set_trace()

        ## Need to get relationship columns for primary keys!

        instance = None
        try:
            q = self.session.query(self.opts.model).filter_by(**filters)
            assert q.count() <= 1
            instance = q.first()
            print(filters, instance)
        except StatementError:
            pass
        if instance is None:
            return super().get_instance(data)

        return instance

    # @pre_load
    # def set_preload(self, data, **kwargs):
    #     #import pdb; pdb.set_trace()
    #     #q = self.session.query(self.opts.model)
    #
    #     if self._simple is None:
    #         return
    #
    #     v = self._simple.load(data, session=self.session, partial=True)
    #     import pdb; pdb.set_trace()
    #
    #     # #self.fields['children'].schema.session = self.session
    #     # for key, field in self.fields.items():
    #     #     if isinstance(field, Nested):
    #     #         # Can't filter on nested fields just yet, since they aren't loaded.
    #     #         continue
    #     #     val = data.get(field.data_key)
    #     #     prop = getattr(self.opts.model, 'key')
    #     #     q = q.filter()
    #     #     import pdb; pdb.set_trace()
    #     #

    @pre_load
    def expand_primary_keys(self, value, **kwargs):
        try:
            # Typically, we are deserializing from a mapping of values
            return dict(**value)
        except TypeError:
            pass
        val_list = ensure_list(value)
        model = self.opts.model
        pk = get_primary_keys(model)
        assert len(pk) == len(val_list)
        res = {}
        for col, val in zip(pk, val_list):
            res[col.key] = val
        return res

    @post_load
    def make_instance(self, data, **kwargs):
        print("Making instance of ", self.opts.model)
        inst = super().make_instance(data, **kwargs)
        #self.session.add(inst)
        return inst

    def to_json_schema(model):
        return json_schema.dump(model)

    from .display import pretty_print


def model_interface(model, session=None):
    """
    Create a Marshmallow interface to a SQLAlchemy model
    """
    # Create a meta class
    metacls = type("Meta", (BaseMeta,), dict(
                    model=model,
                    sqla_session=session))

    schema_name = to_schema_name(model.__name__)
    try:
        # All conversion logic comes from ModelSchema
        return type(schema_name, (BaseSchema,), {'Meta': metacls})
    except exceptions.ModelConversionError as err:
        secho(type(err).__name__+": "+schema_name+" - "+str(err), fg='red')
        return None


class InterfaceCollection(ModelCollection):
    def register(self, *classes):
        for cls in classes:
            self._register_model(cls)

    def _register_model(self, cls):
        k = classname_for_table(cls.__table__)
        # Bail if we have a view
        if not hasattr(cls, '__mapper__'):
            return
        self.add(k, model_interface(cls))


class InterfacePlugin(SparrowCorePlugin):
    name = "schema-interface"

    def on_database_ready(self):
        iface = InterfaceCollection(self.app.database.model)
        db = self.app.database
        db.interface = iface

    def on_setup_cli(self, cli):
        from .cli import show_interface
        cli.add_command(show_interface)


def load_data(mapping):
    from ..app import construct_app
    app, db = construct_app()
    print(mapping)


# transient load
# https://marshmallow-sqlalchemy.readthedocs.io/en/latest/recipes.html#smart-nested-field
# schema().load({}, transient=True)
