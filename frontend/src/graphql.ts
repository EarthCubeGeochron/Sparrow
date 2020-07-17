import GraphiQL from 'graphiql';
import fetch from 'isomorphic-fetch';
import h from 'react-hyperscript'
import "graphiql/graphiql.min.css"
import "./main.styl"

async function graphQLFetcher(graphQLParams) {
  const res = await fetch('/graphql', {
    method: 'post',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(graphQLParams),
  })
  return res.json();
}

const GraphQLExplorer = ()=>h(GraphiQL, {fetcher: graphQLFetcher});

export default GraphQLExplorer
