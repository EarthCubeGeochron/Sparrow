from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Related
from marshmallow.fields import Nested
from marshmallow_jsonschema import JSONSchema
from marshmallow_sqlalchemy.fields import get_primary_keys, ensure_list
from marshmallow.decorators import pre_load, post_load, post_dump
from sqlalchemy.orm import RelationshipProperty
from collections.abc import Mapping
from sqlalchemy import inspect

from ..exceptions import SparrowSchemaError
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

    @property
    def _table(self):
        return self.opts.model.__table__

    def _build_filters(self, data):
        # Filter on properties that actually have a local column
        filters = {}

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
            return filters

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
                    filters[prop.key] = val
            elif hasattr(prop, "direction"):
                # This is unsatisfying, as we can't filter on pre-existing
                # related fields
                filters[prop.key] = None
        return filters

    def load(self, data, **kwargs):
        if self.session is None:
            return super().load(data, **kwargs)
        with self.session.no_autoflush:
            return super().load(data, **kwargs)

    def _get_instance(self, data):
        """Gets pre-existing instances if they are available."""

        if isinstance(data, self.opts.model):
            return data

        filters = self._build_filters(data)

        # Create "fast paths" to make sure we don't grab data and analysis
        # if they aren't properly linked. NOTE: we can probably solve this
        # in general by requiring nullable foreign keys to be specified
        if self.opts.model.__name__ == "datum":
            if filters.get("_analysis") is None:
                return None

        if self.opts.model.__name__ == "analysis":
            if filters.get("_session") is None:
                return None

        msg = f"Finding instance of {self.opts.model.__name__}"

        with self.session.no_autoflush:
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
            log.debug(data)
        return super().get_instance(data)

    @pre_load
    def expand_primary_keys(self, value, **kwargs):
        # If we have a database model, leave it alone.
        if isinstance(value, self.opts.model) or isinstance(value, Mapping):
            return value

        pk_vals = ensure_list(value)
        # log.debug("Expanding keys " + str(pk_vals))

        pk = get_primary_keys(self.opts.model)
        try:
            assert len(pk) == len(pk_vals)
        except AssertionError:
            raise SparrowSchemaError(f"Could not expand primary key for {self.opts.model.__name__} from {value}")
        return {col.key: val for col, val in zip(pk, pk_vals)}

    @post_load
    def make_instance(self, data, **kwargs):
        # Find instance in cache
        cache_key = None
        try:
            cache_key = hash(frozenset(data.items()))
            match_ = self.__instance_cache.get(cache_key, None)
            if match_ is not None:
                log.debug(
                    f"Found {match_} in session cache for {data} (key: {cache_key})"
                )
                return match_
        except TypeError:
            pass

        instance = self._get_instance(data)
        if instance is None:
            instance = self.opts.model(**data)
            self.session.add(instance)
        if cache_key is not None:
            self.__instance_cache[cache_key] = instance
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
