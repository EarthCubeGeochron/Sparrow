from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Related
from marshmallow.fields import Nested
from marshmallow_jsonschema import JSONSchema
from marshmallow_sqlalchemy.fields import get_primary_keys, ensure_list
from marshmallow.decorators import pre_load, post_load, post_dump
from sqlalchemy.exc import StatementError, IntegrityError
from sqlalchemy.orm.exc import FlushError
from sqlalchemy.orm import RelationshipProperty
from collections.abc import Mapping
from sqlalchemy import inspect

from .util import is_pk_defined, pk_values, prop_is_required
from .converter import SparrowConverter, allow_nest

from sparrow import get_logger

log = get_logger(__name__)


def _jsonschema_type_mapping(self):
    """TODO: this is just a shim"""
    return {"type": "integer"}


Related._jsonschema_type_mapping = _jsonschema_type_mapping
Nested._jsonschema_type_mapping = _jsonschema_type_mapping

json_schema = JSONSchema()


class BaseMeta:
    model_converter = SparrowConverter
    # Needed for SQLAlchemyAutoSchema
    include_relationships = True
    load_instance = True


def is_model_ready(model, data):
    mapper = inspect(model)
    required_props = [a for a in mapper.attrs if prop_is_required(a)]
    for attr in required_props:
        val = data.get(attr.key, None)
        if val is None:
            return False
    return True


def matches(instance, filters):
    for k, v in filters.items():
        try:
            if getattr(instance, k) != v:
                return False
        except AttributeError:
            return False
    return True


class ModelSchema(SQLAlchemyAutoSchema):
    """
    :param: allowed_nests: List of strings or "all"
    """

    def __init__(self, *args, **kwargs):
        kwargs["unknown"] = True
        nests = kwargs.pop("allowed_nests", [])
        self.allowed_nests = nests
        if len(self.allowed_nests) > 0:
            model = self.opts.model.__name__
            log.debug(
                f"\nSetting up schema for model {model}\n  allowed nests: {nests}"
            )

        self._show_audit_id = kwargs.pop("audit_id", False)
        self.__instance_cache = {}

        super().__init__(*args, **kwargs)

    def _ready_for_flush(self, instance):
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

    def _build_filters(self, data):
        # Filter on properties that actually have a local column
        filters = {}
        related_models = {}

        # Try to get filters for unique and pk columns first
        for prop in self.opts.model.__mapper__.iterate_properties:
            columns = getattr(prop, "columns", False)
            if columns:
                is_fully_defined = all(
                    [any([c.primary_key, c.unique]) for c in columns]
                )
                # Shim for the fact that we don't correctly find Session.uuid as unique at the moment...
                # TODO: fix this in general
                # if self.opts.model.__name__ == "Session" and prop.key == "uuid":
                #    is_fully_defined = True
                if is_fully_defined:
                    val = data.get(prop.key, None)
                    if val is not None:
                        filters[prop.key] = val
        if filters:
            return filters, related_models

        for prop in self.opts.model.__mapper__.iterate_properties:
            val = data.get(prop.key, None)
            if getattr(prop, "uselist", False):
                continue

            if val is not None:
                if hasattr(prop, "direction"):
                    # For relationships
                    if is_pk_defined(val):
                        filters[prop.key] = val
                    else:
                        related_models[prop.key] = val
                else:
                    filters[prop.key] = val
            elif hasattr(prop, "direction"):
                # This is unsatisfying, as we can't filter on pre-existing
                # related fields
                filters[prop.key] = None
        return filters, related_models

    def _get_instance(self, data):
        """Gets pre-existing instances if they are available."""

        if isinstance(data, self.opts.model):
            return data

        filters, related_models = self._build_filters(data)

        msg = f"Finding instance of {self.opts.model.__name__}"

        # Need to get relationship columns for primary keys!
        query = self.session.query(self.opts.model).filter_by(**filters)
        instance = query.first()

        if instance is not None:
            log.debug(msg + f"...success!\n...filters: {filters}")
            for k, v in data.items():
                setattr(instance, k, v)
            return instance
        else:
            log.debug(msg + f"...none found\n...filters: {filters}")
        return super().get_instance(data)

    @pre_load
    def expand_primary_keys(self, value, **kwargs):
        # If we have a database model, leave it alone.
        if isinstance(value, self.opts.model) or isinstance(value, Mapping):
            return value

        pk_vals = ensure_list(value)
        log.debug("Expanding keys " + str(pk_vals))

        pk = get_primary_keys(self.opts.model)
        assert len(pk) == len(pk_vals)
        return {col.key: val for col, val in zip(pk, pk_vals)}

    @post_load
    def make_instance(self, data, **kwargs):
        instance = self._get_instance(data)

        if instance is not None:
            return instance

        try:
            # Begin a nested subtransaction
            with self.session.begin_nested():
                instance = self.opts.model(**data)
                log.debug(f"Created instance {instance} with parameters {data}")
                self.session.add(instance)
                self.session.flush(objects=[instance])
                log.debug(f"Successfully persisted {instance} to database")
        except (IntegrityError, FlushError) as err:
            log.debug("Could not persist")
        return instance

    @post_dump
    def remove_internal_fields(self, data, many, **kwargs):
        if not self._show_audit_id:
            data.pop("audit_id", None)
        return data

    def to_json_schema(self, model):
        return json_schema.dump(model)

    def _available_nests(self):
        model = self.opts.model
        nests = []
        for prop in model.__mapper__.iterate_properties:
            if not isinstance(prop, RelationshipProperty):
                continue
            if allow_nest(model.__table__.name, prop.target.name):
                nests.append(prop.target.name)
        return nests

    from .display import pretty_print
