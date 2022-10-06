from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Related
from marshmallow.fields import Nested
from marshmallow_jsonschema import JSONSchema
from marshmallow_sqlalchemy.fields import get_primary_keys, ensure_list
from marshmallow.decorators import pre_load, post_load, post_dump
from sqlalchemy.orm import RelationshipProperty, joinedload, defer
from collections.abc import Mapping
from sqlalchemy import inspect

from .fields import SmartNested
from .util import is_pk_defined, pk_values, prop_is_required
from .converter import SparrowConverter, allow_nest, exclude_fields

from macrostrat.utils import get_logger

log = get_logger(__name__)


class SparrowSchemaError(Exception):
    ...


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

    # A list of SQLAlchemy collections that we are nesting on
    nest_collections = []

    def __init__(self, *args, **kwargs):
        kwargs["unknown"] = True
        nests = kwargs.pop("allowed_nests", [])
        self.allowed_nests = nests
        model = self.opts.model.__name__
        _message = f"Setting up schema for model {model}"
        if len(self.allowed_nests) > 0:
            _message += f" with allowed nests: {nests}"
            log.debug(_message)

        # Excluding kinda works but still pulls back fields into schema
        self._deferred_fields = [
            *kwargs.get("exclude", []),
            # Global defer list (we should refactor this eventually)
            *exclude_fields.get(model, []),
        ]
        # log.debug(_message)
        self._show_audit_id = kwargs.pop("audit_id", False)
        self.__instance_cache = {}

        self._mapper = self.opts.model.__mapper__
        super().__init__(*args, **kwargs)

    @classmethod
    def query(cls, session):
        """A helper that allows query objects to be constructed:
        `UserSchema.query(db.session).all()`
        """
        return session.query(cls.opts.model)

    @classmethod
    def table_name(cls):
        return cls.opts.model.__table__.name

    @property
    def _table(self):
        return self.opts.model.__table__

    def _nested_relationships(self, *, nests=None, current_depth=0, max_depth=None):
        """Get relationship fields for nested models, allowing them
        to be pre-joined.

        kwargs:
        mode [nested, related, hybrid]
            - nested: loads only the models directly referenced in nests
            - related: loads all models, even those referenced in related models only
            - hybrid [default]: loads all models, attempting to pull back only needed
                attributes that define the relationship...
        """
        depth = current_depth
        if max_depth != None and depth > max_depth:
            return [], None
        # It would be nice if we didn't have to pass nests down here...
        _nests = nests or self.allowed_nests
        for key, field in self.fields.items():

            if not isinstance(field, Related):
                continue
            # Yield this relationship
            this_relationship = getattr(self.opts.model, key)

            nested = isinstance(field, SmartNested) and field._should_nest()

            ##load_hint needs to be the attribute of the model joining
            load_hint = None
            # We are passing through load_hints to allow us to
            # return only a subset of columns when primary keys are
            # desired.
            # if not nested:
            #    load_hint = this_relationship.property.remote_side

            yield [this_relationship], load_hint
            if not nested:
                continue
            # We're only working with nested fields now
            field.schema.allowed_nests = _nests
            # Get relationships from nested models
            for rel, load_hint in field.schema._nested_relationships(
                nests=_nests, current_depth=depth + 1, max_depth=max_depth
            ):
                yield [this_relationship, *rel], load_hint

    def query_options(self, max_depth=None):
        for rel, load_hint in self._nested_relationships(max_depth=max_depth):
            res = joinedload(*rel)
            if load_hint is not None:
                res = res.load_only(*list(load_hint))
            yield res
        # Defer excluded fields
        # Results in a huge speedup if fields are sizeable
        for field in self._deferred_fields:
            yield defer(field)

    def nested_relationships(self, max_depth=None):
        return [v for v, _ in self._nested_relationships(max_depth=max_depth)]

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

        if self.instance is not None:
            return self.instance

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
                log.info(msg + f"...success!\n...filters: {filters}")
                for k, v in data.items():
                    setattr(instance, k, v)
                return instance
            else:
                log.info(msg + f"...none found\n...filters: {filters}")
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
            raise SparrowSchemaError(
                f"Could not expand primary key for {self.opts.model.__name__} from {value}"
            )
        return {col.key: val for col, val in zip(pk, pk_vals)}

    def _get_cached_instance(self, data):
        """Get an instance cached within this load transaction"""
        cache_key = None
        try:
            cache_key = hash(frozenset(data.items()))
            match_ = self.__instance_cache.get(cache_key, None)
            if match_ is not None:
                log.debug(
                    f"Found {match_} in session cache for {data} (key: {cache_key})"
                )
                return match_, cache_key
        except TypeError:
            pass
        return None, cache_key

    @post_load
    def make_instance(self, data, **kwargs):
        # We start off with no instance loaded
        instance = None
        # FIRST, try to load from cached values created during this import
        #
        # This cache exists primarily to cover cases where we import models that need to be
        # linked in multiple places (e.g. units, parameters, and datum_types). We could potentially
        # expand it to cover cases where we want to create several models up front and then reference
        # them from other places in the import model hierarchy.
        #
        # Datum (and some other analytical models) can easily be pulled in without a specific provided
        # identity (they get their uniqueness in part from their link to analysis). Given this,
        # it is possible for us to "steal" them from other analyses imported
        # at the same time. It's likely this could happen with analysis and other models as well.
        #
        # See https://github.com/EarthCubeGeochron/Sparrow/issues/80
        #
        # We solve this by exempting these models from caching. However, there are
        # likely more issues that will arise along these lines in the near future.
        cache_key = None
        # We should figure out a better way to do this than a blacklist...or at
        # least pull the blacklist into config code somewhere.
        _cache_blacklist = ["datum", "analysis", "session", "sample"]
        if self.opts.model.__name__ not in _cache_blacklist:
            instance, cache_key = self._get_cached_instance(data)

        # THEN, try to load from existing instances
        if instance is None and not self.transient:
            instance = self._get_instance(data)

        # FINALLY, make a new instance if one can't be found
        if instance is None:
            instance = self.opts.model(**data)
            if self.session is not None:
                log.debug(f"Adding new {instance} to session")
                self.session.add(instance)
        if cache_key is not None:
            self.__instance_cache[cache_key] = instance
        return instance

    @post_dump
    def remove_internal_fields(self, data, many, **kwargs):
        if not self._show_audit_id:
            data.pop("pgmemento_audit_id", None)
        return data

    def to_json_schema(self, model):
        return json_schema.dump(model)

    def _nest_relationships(self):
        model = self.opts.model
        nests = []
        for prop in model.__mapper__.iterate_properties:
            if not isinstance(prop, RelationshipProperty):
                continue
            if allow_nest(model.__table__.name, prop.target.name):
                nests.append(prop)
        return nests

    def _available_nests(self):
        return [rel.target.name for rel in self._nest_relationships()]

    from .display import pretty_print
