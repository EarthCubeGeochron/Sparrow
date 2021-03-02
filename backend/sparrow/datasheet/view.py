from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.routing import Route, Router
from starlette.responses import PlainTextResponse, JSONResponse, Response
from ..context import app_context
from sqlalchemy import create_engine, MetaData, Table, Column
import pandas as pd
import json
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import mapping, shape, Point
from webargs import fields
from webargs_starlette import use_annotations
import pandas as pd

user_args = {
    "groupby": fields.String(missing='Project')
}

@use_annotations(location='query')
##async def datasheet_view(request, name: str): Can take query params out in args
async def datasheet_view(request):
    '''
        Unique api endpoint to gather data specific to the datasheet U.I

        Goals: responds with data from database to show on U.I
            - Sample ID
            - Sample Name
            - Sample material
            - Sample Location
            - Project
            - DOI/publication: pass a list if multiple

        FUTURE GOALS: Groupby funcationality that allows for incoming results
        to be grouped by a feature (i.e project), maype some other functionality
    '''
    # TODO: I'm gonna need a widget to look up all the info from an edited DOI to fill in the rest
    # of the database table fields. Bib-json, pand docs
    
    db = app_context().database

    ## This query does all that crazy pandas stuff that I would have had to done.
    ## A lot less code
    query = '''WITH A AS(
SELECT
  s.id,
  s.name,
  s.material,
  ST_AsGeoJSON(s.location)::jsonb geometry,
  array_agg(DISTINCT p.id) AS project_id,
  array_agg(DISTINCT p.name) AS project_name,
  array_agg(DISTINCT pub.id) AS publication_id,
  array_agg(DISTINCT pub.doi) AS doi
FROM sample s
LEFT JOIN session ss
  ON s.id = ss.sample_id
LEFT JOIN project p
  ON ss.project_id = p.id
LEFT JOIN project_publication proj_pub
  on p.id = proj_pub.project_id
LEFT JOIN publication pub
  ON proj_pub.publication_id = pub.id
GROUP BY s.id)
  SELECT DISTINCT * 
  FROM A
  ORDER BY A.id;
'''

    test = pd.read_sql(query, db.engine.connect())
    
    res = test.to_json(orient='records')

    return JSONResponse(json.loads(res))