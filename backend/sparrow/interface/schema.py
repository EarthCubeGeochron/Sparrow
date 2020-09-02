from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Related
from marshmallow.fields import Nested
from marshmallow_jsonschema import JSONSchema
from marshmallow_sqlalchemy.fields import get_primary_keys, ensure_list
from marshmallow.decorators import pre_load, post_load, post_dump
from sqlalchemy.exc import StatementError, IntegrityError

from .util import is_pk_defined, pk_values, prop_is_required
from .converter import SparrowConverter

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


class ModelSchema(SQLAlchemyAutoSchema):
    value_index = {}

    def __init__(self, *args, **kwargs):
        self.allowed_nests = kwargs.pop("allowed_nests", [])
        self._show_audit_id = kwargs.pop("audit_id", False)

        super().__init__(*args, **kwargs)

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
        sess = self.session
        for inst in list(sess.new):
            if not isinstance(inst, self.opts.model):
                continue
            for k, value in filters.items():
                if value != getattr(inst, k):
                    return None
            log.debug(f"Found instance {inst} in session")
            return inst
        return None

    def _build_filters(self, data):
        # Filter on properties that actually have a local column
        filters = {}
        related_models = {}
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

        filters, related_models = self._build_filters(data)

        # Try to get value from session
        log.debug(f"Finding instance of {self.opts.model.__name__}")
        log.debug(f"..filters: {filters}")
        instance = self._get_session_instance(filters)

        # Need to get relationship columns for primary keys!
        if instance is None:
            try:
                query = self.session.query(self.opts.model).filter_by(**filters)
                instance = query.first()
                if instance is None:
                    log.debug("..none found")
                else:
                    log.debug("..success!")
            except StatementError:
                log.exception("..none found")
        if instance is None:
            instance = super().get_instance(data)

        if instance is not None:
            for k, v in related_models.items():
                setattr(instance, k, v)

        # Get rid of filters by value
        # if self.opts.model.__name__ == 'analysis':
        #     print(filters)
        #     import pdb; pdb.set_trace()

        return instance

    @pre_load
    def expand_primary_keys(self, value, **kwargs):
        try:
            # Typically, we are deserializing from a mapping of values
            return dict(**value)
        except TypeError:
            pass
        val_list = ensure_list(value)
        log.debug("Expanding keys " + str(val_list))

        model = self.opts.model
        pk = get_primary_keys(model)
        assert len(pk) == len(val_list)
        res = {}
        for col, val in zip(pk, val_list):
            res[col.key] = val
        return res

    @post_load
    def make_instance(self, data, **kwargs):
        instance = self._get_instance(data)
        if instance is None:
            try:
                # Begin a nested subtransaction
                self.session.begin_nested()
                instance = self.opts.model(**data)
                self.session.add(instance)
                log.debug(f"Created instance {instance} with parameters {data}")
                # self.session.flush(objects=[instance])
                self.session.commit()
                log.debug("Successfully persisted to database")
            except IntegrityError as err:
                self.session.rollback()
                log.debug("Could not persist but will try again later")
                log.debug(err)

        return instance

    @post_dump
    def remove_internal_fields(self, data, many, **kwargs):
        if not self._show_audit_id:
            data.pop("audit_id")
        return data

    def to_json_schema(model):
        return json_schema.dump(model)

    from .display import pretty_print
