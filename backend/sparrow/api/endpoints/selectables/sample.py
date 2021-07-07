from os import RTLD_NOW, error
from starlette.endpoints import HTTPEndpoint
from starlette.routing import Route, Router
from webargs_starlette import parser
from sqlakeyset import select_page
from starlette.responses import JSONResponse
from webargs.fields import Str, Int, Boolean, DelimitedList
from sqlalchemy.sql import text, select
from sparrow.context import get_database
from ...exceptions import ValidationError
from ...response import APIResponse

class SubSamples(HTTPEndpoint):
    """ 
    Endpoint to retrieve subsamples, i.e sample collections
    
    sample_collection not coming through in normal api for sample model
    """

    async def get(self, request):
        db = get_database()
        sample = db.model.sample
        sampleSchema = db.interface.sample(many=True)

        if 'id' not in request.path_params:
            return JSONResponse({})

        id_ = request.path_params['id']

        sample_ = db.session.query(sample).get(id_)

        if len(sample_.sample_collection) == 0:
            return JSONResponse({'id':id_, 'sample_collection': []})

        sample_collection = sampleSchema.dump(sample_.sample_collection)

        return JSONResponse({'id':id_, 'sample_collection': sample_collection})