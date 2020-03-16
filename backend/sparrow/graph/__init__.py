from flask_graphql import GraphQLView
from ..plugins import SparrowCorePlugin
from .schema import build_schema

class GraphQLPlugin(SparrowCorePlugin):
    name = "graphql"
    def on_finalize_routes(self):
        db = self.app.database
        ctx = dict(session=db.session)
        s = build_schema(db)
        graphql = GraphQLView.as_view('graphql',
                                        schema=s,
                                        graphiql=True,
                                        context=ctx)

        self.app.add_url_rule('/graphql', view_func=graphql)
