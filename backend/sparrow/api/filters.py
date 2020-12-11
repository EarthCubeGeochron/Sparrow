from webargs.fields import DelimitedList, Str, Int, Boolean, DateTime
from .exceptions import ValidationError
from sqlalchemy import and_
import datetime

def _schema_fields(schema):
    return {getattr(f, "data_key", k): f for k, f in schema.fields.items()}


class BaseFilter:
    params = None
    help = None

    def __init__(self, model, schema=None):
        self.model = model
        self.schema = schema

    def should_apply(self):
        return True

    def apply(self, query, args):
        return query

    def __call__(self, query, args):
        if not self.should_apply():
            return query
        return self.apply(args, query)


class AuthorityFilter(BaseFilter):
    params = dict(authority=Str(missing=None))
    help = dict(authority="Authority")

    def should_apply(self):
        return hasattr(self.model, "authority")

    def apply(self, args, query):
        if args["authority"] is None:
            return query
        return query.filter(self.model.authority == args["authority"])


class FieldExistsFilter(BaseFilter):
    key = "has"

    @property
    def params(self):
        return {
            self.key: DelimitedList(
                Str(), missing=[], description="filter by [field] existence"
            )
        }

    def should_apply(self):
        """This only works with objects defined with a schema for now"""
        return self.schema is not None

    def _field_filter(self, field):
        orm_attr = getattr(self.model, field.name)
        if hasattr(field, "related_model"):
            if orm_attr.property.uselist:
                return orm_attr.any()
            else:
                return orm_attr.has()
        return orm_attr.isnot(None)

    def apply(self, args, query):
        fields = _schema_fields(self.schema())
        # Filter by has
        for has_field in args[self.key]:
            try:
                field = fields[has_field]
            except KeyError:
                raise ValidationError(f"'{has_field}' is not a valid field")
            query = query.filter(self._field_filter(field))
        return query


class FieldNotExistsFilter(FieldExistsFilter):
    key = "not_has"

    def _field_filter(self, field):
        orm_attr = getattr(self.model, field.name)
        if hasattr(field, "related_model"):
            if orm_attr.property.uselist:
                return ~orm_attr.any()
            else:
                return ~orm_attr.has()
        return orm_attr.is_(None)

class EmbargoFilter(BaseFilter):
    key = "public"
    
    @property
    def params(self):
        return {
            self.key: Boolean(
                 description="filter by embargoed or not, (false = private data, true = public data, empty = all data)"
            )
        }
    
    def should_apply(self):
        '''Whichever models have a field for public'''
        return hasattr(self.model, "embargo_date")
    
    def apply(self, args, query):
        '''Where the sausage gets made'''

        if self.key not in args:
            return query

        arg = args[self.key] ## either true, false or empty.

        if arg: 
            return query.filter(self.model.embargo_date == None)
        else:
            return query.filter(self.model.embargo_date != None)
    
class DateFilter(BaseFilter):
    '''
        Filter to get dates inbetween two dates passed to API
        if start, end, and date are datetime objects then I can do this:
            if start < date < end:
                return True

        for datetime formating we will assume, for now that frontend is passing:
            2014-06-12/13:23:06 for format %Y-%m-%d/%H:%M:%S
    '''
    key='date_range'

    @property
    def params(self):
        return{
            self.key : DelimitedList(
                Str(), 
                description="Filter by date or date range, ex: date_range=2013-03-23/14:23:03,2013-05-01/06:00:00 where the format is YYYY-MM-DD/H:M:S"
            )
        }

    def should_apply(self):
        return hasattr(self.model, "date")

    def apply(self, args, query):
        if self.key not in args:
            return query

        format = "%Y-%m-%d/%H:%M:%S"

        start, end = args[self.key]
        start = datetime.datetime.strptime(start, format)
        end = datetime.datetime.strptime(end, format)

        
        return query.filter(and_(self.model.date > start, self.model.date < end))


'''
    Filters we want to add:
    - Fuzzy searches, as type for something, 
      i.e a material in an input, dropdown results are materials that closest match.
      Or entering a sample, session, project, etc.. name on that search bar for the admin pages
    - SQLAlchemy filtering (like, match)

    Register Filter infrastructure:
    - Location filter: Draw Box on map, or enter in 4 cooridnates
    - Search by DOI on project page
         - query.filter(self.model.like/match(search_str))

    Updating help pages on API

    Issues: not having a should_apply function creates an error with line 184 in model.py

    
    Two Separate Filters:
        - Open ended searching through postgres.
            - Search that isn't confined to specific model
                - Database problem... postgres open search
                - Join all info from table columns into 1 large searchable string

        - Specific filtering capabilities similar to this page's classes.
'''