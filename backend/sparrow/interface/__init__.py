from sparrow.plugins import SparrowCorePlugin
from sparrow.database.mapper import BaseModel
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, exceptions
from marshmallow_sqlalchemy.fields import Related
from marshmallow.fields import Nested
from marshmallow_jsonschema import JSONSchema
from marshmallow_sqlalchemy.fields import get_primary_keys, ensure_list
from marshmallow.decorators import pre_load, post_load
from sqlalchemy.exc import StatementError, IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import FlushError
from click import secho

from .converter import SparrowConverter, to_schema_name
from .util import column_is_required
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


def columns_for_prop(prop):
    try:
        return getattr(prop, 'columns')
    except AttributeError:
        return list(getattr(prop, 'local_columns'))


def prop_is_required(prop):
    cols = [column_is_required(c) for c in columns_for_prop(prop)]
    return any(cols)


def pk_values(instance):
    props = get_primary_keys(instance.__class__)
    keys = {prop.key: getattr(instance, prop.key) for prop in props}
    return keys.values()


def pk_data(model, data):
    props = get_primary_keys(model)
    keys = {prop.key: data.get(prop.key) for prop in props}
    return keys.values()


def is_pk_defined(instance):
    vals = pk_values(instance)
    return all([v is not None for v in vals])


class BaseSchema(SQLAlchemyAutoSchema):
    value_index = {}
    def _ready_for_flush(self, instance):
        if instance is None:
            return False
        if any([p is None for p in pk_values(instance)]):
            return False
        for prop in self.opts.model.__mapper__.iterate_properties:
            is_required = prop_is_required(prop)
            if not is_required:
                continue
            if getattr(instance, prop.key, None) is None:
                return False

        return True

    @property
    def _table(self):
        return self.opts.model.__table__

    def _get_session_instance(self, filters):
        sess = self.session()
        for inst in list(sess.new):
            if not isinstance(inst, self.opts.model):
                continue
            for k, value in filters.items():
                if value != getattr(inst, k):
                    return None
            log.debug(f"Found instance {inst} in session")
            return inst
        return None

    def _get_instance(self, data):
        """Gets pre-existing instances if they are available."""
        pk = tuple(pk_data(self.opts.model, data))
        pk_is_defined = all([k is not None for k in pk])

        # Filter on properties that actually have a local column
        filters = {}
        related_models = {}
        instance = None
        for prop in self.opts.model.__mapper__.iterate_properties:
            val = data.get(prop.key, None)
            if getattr(prop, 'uselist', False):
                continue
            if val is not None:
                if hasattr(prop, 'direction'):
                    # For relationships
                    if is_pk_defined(val):
                        filters[prop.key] = val
                    else:
                        related_models[prop.key] = val
                else:
                    filters[prop.key] = val
            else:
                # Required column is unset
                # cols = columns_for_prop(prop)
                if hasattr(prop, 'direction'):
                    # This is unsatisfying, as we can't filter on pre-existing
                    # related fields
                    filters[prop.key] = None
                # is_required = any([column_is_required(i) for i in cols])
                # if is_required:
                #     if len(cols[0].foreign_keys) > 0:
                #         continue
                #     #instance = super().get_instance(data)

        # Try to get value from session
        if instance is None:
            log.debug(f"Finding instance of {self.opts.model.__name__}")
            log.debug(f"..filters: {filters}")
            instance = self._get_session_instance(filters)

        # Get rid of filters by value

        # Need to get relationship columns for primary keys!
        if instance is None:
            try:
                query = self.session.query(self.opts.model).filter_by(**filters)
                instance = query.one_or_none()
                if instance is None:
                    log.debug("..none found")
                else:
                    log.debug("..success!")
            except StatementError as err:
                log.exception(f"..none found")
        if instance is None:
            instance = super().get_instance(data)

        if instance is not None:
            for k, v in related_models.items():
                setattr(instance, k, v)

        return instance

    @pre_load
    def expand_primary_keys(self, value, **kwargs):
        try:
            # Typically, we are deserializing from a mapping of values
            return dict(**value)
        except TypeError:
            pass
        val_list = ensure_list(value)
        log.debug("Expanding keys "+str(val_list))

        model = self.opts.model
        pk = get_primary_keys(model)
        assert len(pk) == len(val_list)
        res = {}
        for col, val in zip(pk, val_list):
            res[col.key] = val
        return res

    @post_load
    def make_instance(self, data, **kwargs):
        #data_key = hash(frozenset(data))
        #instance = self.value_index.get(data_key, None)

        #if instance is None:
        instance = self._get_instance(data)
        if instance is None:
            instance = self.opts.model(**data)
            self.session.add(instance)
        #
        # if self._ready_for_flush(instance):
        #     try:
        #         self.session.flush()
        #     except Exception as err:
        #         self.session.rollback()

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
