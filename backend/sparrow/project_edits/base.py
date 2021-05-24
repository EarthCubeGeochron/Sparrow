from starlette.endpoints import HTTPEndpoint
from starlette.routing import Route, Router
from starlette.responses import JSONResponse
from starlette.authentication import requires

from ..context import app_context

## TODO: way to delete publications from this route
# maybe have an actions field for query, one would be delete, if that was there it would call a function
# that handles removing that relationship from project.
# PROBLEM: This solution won't remove the publication completely, as it shouldn't in a real world senario.
# it just removes the foreign id reference. We'll have to just remove them with a quick algorithim or something


class ProjectEdits(HTTPEndpoint):
    @requires("admin")
    async def put(self, request):
        """
        Improved endpoint for Admin Projects page. Using Schemas

        Things that need to be done. Check for collection changes.
            Researcher
            Publication
            Samples**
            Sessions**
        **: need to handle internal changes to model, i.e session's sample can be changed on project adim

        all need to support adding new instances except sessions.
        db.model_schema
        """
        db = app_context().database
        project_schema = db.interface.project()
        project = db.model.project

        proj_id = request.path_params["id"]
        existing_project = project.query.get(proj_id)

        updates = await request.json()
        updates.pop("id")

        new_proj = project_schema.load(updates, session=db.session)
        new_proj.id = existing_project.id

        db.session.rollback()
        res = db.session.merge(new_proj)
        db.session.commit()

        proj_final = project_schema.dump(res)

        return JSONResponse({"Status": "Success", "data": proj_final})


Project_edits_api = Router(
    [
        Route("/edit/{id}", endpoint=ProjectEdits, methods=["PUT"]),
    ]
)
