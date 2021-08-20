from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from sparrow.context import get_database
from ...exceptions import ApplicationError
from ..base import BaseEndpoint


class SubSamples(BaseEndpoint):
    """
    Endpoint to retrieve subsamples, i.e sample collections

    sample_collection not coming through in normal api for sample model
    """

    def __init__(self, *args, **kwargs):
        self.model = get_database().model.sample
        self.schema = get_database().interface.sample
        super().__init__(*args, **kwargs)

    async def get(self, request):
        db = get_database()
        sample = db.model.sample
        sampleSchema = db.interface.sample(many=True)

        if "id" not in request.path_params:
            return JSONResponse({})

        id_ = request.path_params["id"]

        sample_ = db.session.query(sample).get(id_)

        if len(sample_.sample_collection) == 0:
            return JSONResponse({"id": id_, "sample_collection": []})

        sample_collection = sampleSchema.dump(sample_.sample_collection)

        return JSONResponse({"id": id_, "sample_collection": sample_collection})

    async def put(self, request):
        db = get_database()
        sample = db.model.sample

        id_ = request.path_params["id"]

        sample_ = db.session.query(sample).get(id_)

        data = await request.json()

        if "member_of" in data:
            member_id = data["member_of"]

            sample_.member_of = member_id

            try:
                db.session.commit()
                return JSONResponse({"id": id_, "member_of": member_id})
            except Exception as err:
                db.session.rollback()
                raise ApplicationError(str(err))


class MapSamples(BaseEndpoint):
    """
    Endpoint for quick loading of samples for locations, on maps specifically

    returns: id, name, location
    """

    def __init__(self, *args, **kwargs):
        self.model = get_database().model.sample
        self.schema = get_database().interface.sample
        super().__init__(*args, **kwargs)

    def form_query(self, db):
        sample = self.model

        q = (
            db.session.query(sample.id, sample.name, sample.location)
            .filter(sample.location != None)
            .order_by(sample.id)
        )

        return q
