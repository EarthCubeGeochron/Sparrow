from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from sparrow.core.context import get_database
from ...exceptions import ApplicationError


class SubSamples(HTTPEndpoint):
    """
    Endpoint to retrieve subsamples, i.e sample collections

    sample_collection not coming through in normal api for sample model
    """

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


class MapSamples(HTTPEndpoint):
    """
    Endpoint for quick loading of samples for locations, on maps specifically

    returns: id, name, location
    """

    async def get(self, request):

        db = get_database()
        sample = db.model.sample
        sampleSchema = db.interface.sample(many=True)

        data = (
            db.session.query(sample.id, sample.name, sample.location)
            .filter(sample.location != None)
            .all()
        )

        json_data = sampleSchema.dump(data)

        return JSONResponse({"data": json_data, "total_count": len(json_data)})
