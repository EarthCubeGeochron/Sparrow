from webargs.fields import DelimitedList, Str, Int, Boolean, DateTime
from .exceptions import ValidationError
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import joinedload
from shapely.geometry import box
from geoalchemy2.shape import from_shape
import datetime

from sparrow.context import app_context
from ..datasheet.utils import create_bound_shape


def _schema_fields(schema):
    return {getattr(f, "data_key", k): f for k, f in schema.fields.items()}

def create_params(description, example):
    '''create param description for api docs'''
    return {"description": description, "example": example}

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
        d =  "filter by [field] existence, will return results where passed fields are not null"
        e = ["?has=name","?has=name,location"]
        des = create_params(d, e)
        return {
            self.key: DelimitedList(
                Str(), missing=[], description=des
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

    @property
    def params(self):
        d =  "filter by [field] existence, will return results where passed fields are null"
        e = ["?not_has=name","?not_has=name,location"]
        des = create_params(d, e)
        return {
            self.key: DelimitedList(
                Str(), missing=[], description=des
            )
        }

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
        d= "filter by embargoed or not, (false = private data, true = public data, empty = all data)"
        e = ["?public=true", "?public=false"]
        des = create_params(d,e)
        return {
            self.key: Boolean(
                 description=des
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
            ## if arg is true, then public only
            ## embargo date is the date at which a datum becomes public
            return query.filter(or_(self.model.embargo_date < datetime.datetime.today(), self.model.embargo_date == None))
        else:
            return query.filter(self.model.embargo_date > datetime.datetime.today())
    
class DateFilter(BaseFilter):
    '''
        Filter to get dates inbetween two dates passed to API
        if start, end, and date are datetime objects then I can do this:
            if start < date < end:
                return True

        for datetime formating we will assume, for now that frontend is passing:
            2014-06-12 for format %Y-%m-%d
    '''

    ## TODO: pass only year and will search of dates in that year, etc...

    key='date_range'

    @property
    def params(self):
        d = "Filter by date or date range where the format is YYYY-MM-DD"
        e = ["?date_range=2013-03-23,2013-05-01"]
        des = create_params(d,e)
        return{
            self.key : DelimitedList(
                Str(), 
                description=des
            )
        }

    def should_apply(self):
        answer = hasattr(self.model, "date") or hasattr(self.model, "session_collection")
        return answer

    def apply(self, args, query):
        if self.key not in args:
            return query

        format = "%Y-%m-%d"

        start, end = args[self.key]
        start = datetime.datetime.strptime(start, format)
        end = datetime.datetime.strptime(end, format)
        
        if hasattr(self.model, "session_collection"):
            db = app_context().database
            Session = db.model.session

            return query.join(self.model.session_collection).filter(and_(Session.date > start, Session.date < end))

        
        return query.filter(and_(self.model.date > start, self.model.date < end))

class DOI_filter(BaseFilter):
    key='doi_like'

    @property
    def params(self):
        d = "Search for field by DOI string, can be whole string or anypart of doi"
        e = ["?doi=10.10", "?doi=10.1130/B31239.1"]
        des = create_params(d,e)
        return{
            self.key: Str(
                description=des
            )
        }

    def should_apply(self):
        answer = hasattr(self.model,"doi") or hasattr(self.model, "publication_collection")
        return answer

    def apply(self, args, query):
        if self.key not in args:
            return query

        doi_string = args[self.key]

        
        if hasattr(self.model, "publication_collection"):

            db = app_context().database

            publication = db.model.publication

            return query.join(self.model.publication_collection).filter(publication.doi.like(f'%{doi_string}%'))

        ## this allows for fuzzy searching
        return query.filter(self.model.doi.like(f'%{doi_string}%'))


class Coordinate_filter(BaseFilter):
    key = 'coordinates'

    @property
    def params(self):
        d= 'Option to filter by coordinates, pass a bounding box, minLong, minLat, maxLong, maxLat'
        e = ["?coordinates=0,0,180,90"]
        des = create_params(d,e)
        return{
            self.key: DelimitedList(
                Str(),
                description = des
            )
        }
    def should_apply(self):
        return hasattr(self.model, "location")
    
    
    def apply(self, args, query):
        if self.key not in args:
            return query
        
        points = args['coordinates'] # should be an array [minLong, minLat, maxLong, maxLat]
        pnts = [int(pnt) for pnt in points]
        bounding_shape = create_bound_shape(pnts)

        # Create issue about SRID (4326)
        return query.filter(bounding_shape.ST_Contains(func.ST_Transform(self.model.location, 4326)))

class Geometry_Filter(BaseFilter):
    key = "geometry"

    @property
    def params(self):
        d = "A string of Well Know Text for a Polygon, circle or box, will return all data located WITHIN the geometry provided. NOTE: do NOT add SRID, assumed SRID of 4326, WGS84 Longitude/Latitude"
        e = ["?geometry=POLYGON((0 0,180 90,180 0,0 90,0 0))"]
        des = create_params(d,e)
        return{
            self.key: Str( description= des)
        }

    def should_apply(self):
        return hasattr(self.model, "location")

    def apply(self, args, query):
        if self.key not in args:
            return query
        
        WKT_shape_text = args[self.key]
        WKT_query = "SRID=4326;" + WKT_shape_text

        
        return query.filter(func.ST_GeomFromEWKT(WKT_query).ST_Contains(func.ST_Transform(self.model.location, 4326)))

## TODO: Age range filter
class Age_Range_Filter(BaseFilter):
    key = "age"

    @property
    def params(self):
        d= "Age of Geologic material, passed in thousand years (ka), can take either range or single number"
        e = ["?age=1200-10000"]
        des = create_params(d,e)
        return{
            self.key: Str(description=des)
            }
    def should_apply(self):
        return hasattr(self.model, "age")
    pass



## TODO: Age range filter, generic parameter filter: pass field and value, Geologic formation filter
## TODO: Define filter in plugin, i.e irradiation filter for WiscAr
## TODO: Filter based on nested models, /api/v2/datum?nest=project,datum_type&datum_type.unit=Ma&project=11

