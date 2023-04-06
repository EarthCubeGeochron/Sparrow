from starlette.responses import JSONResponse
from ..context import app_context
import pandas as pd
import json
from webargs import fields
from webargs_starlette import use_annotations
from ..util import relative_path
from pathlib import Path


user_args = {"groupby": fields.String(missing="Project")}


@use_annotations(location="query")
##async def datasheet_view(request, name: str): Can take query params out in args
async def datasheet_view(request):
    """
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
    """
    # TODO: I'm gonna need a widget to look up all the info from an edited DOI to fill in the rest
    # of the database table fields. Bib-json, pand docs

    db = app_context().database

    p = Path(relative_path(__file__, "queries.sql"))
    sqlfile = open(p, "r")
    query = sqlfile.read()

    test = pd.read_sql(query, db.engine.connect())

    res = test.to_json(orient="records")

    return JSONResponse(json.loads(res))
