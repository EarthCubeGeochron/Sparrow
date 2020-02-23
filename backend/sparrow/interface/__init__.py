from sparrow.plugins import SparrowCorePlugin
from sparrow.database.mapper import BaseModel
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, exceptions
from marshmallow_sqlalchemy.fields import Related
from marshmallow.fields import Nested
from marshmallow_jsonschema import JSONSchema
from marshmallow_sqlalchemy.fields import get_primary_keys, ensure_list
from marshmallow.decorators import pre_load, post_load
from sqlalchemy.exc import StatementError, IntegrityError, InvalidRequestError
from click import secho

from .converter import SparrowConverter, to_schema_name
from ..database.mapper.util import ModelCollection, classname_for_table

from sparrow import get_logger

log = get_logger(__name__)


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
    return not col.nullable and not has_default


def columns_for_prop(prop):
    try:
        return getattr(prop, 'columns')
    except AttributeError:
        return list(getattr(prop, 'local_columns'))

def pk_values(instance):
    props = get_primary_keys(instance.__class__)
    keys = {prop.key: getattr(instance, prop.key) for prop in props}
    return keys.values()

def pk_data(model, data):
    props = get_primary_keys(model)
    keys = {prop.key: data.get(prop.key) for prop in props}
    return keys.values()

class BaseSchema(SQLAlchemyAutoSchema):
    value_index = {}
    def _ready_for_flush(self, instance):
        if instance is None:
            return False
        # for prop in self.opts.model.__mapper__.iterate_properties:
        #     cols = columns_for_prop(prop)
        #     is_required = any([column_is_required(i) for i in cols])
        #     if not is_required:
        #         continue
        #     if getattr(instance, prop.key, None) is None:
        #         return False
        if any([p is None for p in pk_values(instance)]):
            return False

        return True

    @property
    def _table(self):
        return self.opts.model.__table__

    def get_instance(self, data):
        """Gets pre-existing instances if they are available."""
        pk = tuple(pk_data(self.opts.model, data))
        pk_is_defined = all([k is not None for k in pk])

        # Filter on properties that actually have a local column
        filters = {}
        instance = None
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
                    # This is unsatisfying, as we can't filter on pre-existing
                    # related fields
                    filters[prop.key] = None
                is_required = any([column_is_required(i) for i in cols])
                if is_required:
                    if len(cols[0].foreign_keys) > 0:
                        continue
                    instance = super().get_instance(data)

        # Need to get relationship columns for primary keys!
        if instance is None:
            try:
                query = self.session.query(self.opts.model).filter_by(**filters)
                assert query.count() <= 1
                instance = query.first()
            except (StatementError, AssertionError):
                pass
        if instance is None:
            instance = super().get_instance(data)

        if self._ready_for_flush(instance):
            try:
                self.session.flush(objects=[instance])
            except IntegrityError:
                pass

        #    #log.debug(f"Found instance {instance}")
        #    #self.__has_existing = True
        # if pk_is_defined and instance is not None:
        #     # try:
        #     #     with self.session.begin_nested():
        #     self.session.merge(instance)
        #     self.session.flush()
        # except Exception:
        #     pass
        #     log.debug(f"PK defined for {instance} with key {pk}")
        #     self.__class__.value_index[pk_hash] = instance

        return instance

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
        instance = super().make_instance(data, **kwargs)
        # if instance is not None:
        #         self.session.merge(res)
        #         self.session.flush()
        # #
        if self._ready_for_flush(instance):
            try:
                self.session.flush(objects=[instance])
            except IntegrityError:
                pass
            # except InvalidRequestError:
            #     self.session.rollback()
        #if instance is not None:
        # if self._table.name == "datum":
        #     print(data)
        #     from decimal import Decimal
        #     if data['value'] == Decimal('0.383'):
        #         import pdb; pdb.set_trace()
        #
        # if pk_hash not in self.value_index:
        #     #log.debug(f"PK defined for {instance} with key {pk}")
        #     self.value_index[pk_hash] = instance

        return instance

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
