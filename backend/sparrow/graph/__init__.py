from ..plugins import SparrowCorePlugin

class GraphQLPlugin(SparrowCorePlugin):
    name = "graphql"
    def setup_graphql(self):
        from flask_graphql import GraphQLView
        from .schema import build_schema

        ctx = dict(session=self.db.session)
        s = build_schema(self.db)
        view_func = GraphQLView.as_view('graphql',
                                        schema=s,
                                        graphiql=True,
                                        context=ctx)

        self.app.add_url_rule('/graphql', view_func=view_func)

    def on_database_ready(self):
        self.setup_graphql()
