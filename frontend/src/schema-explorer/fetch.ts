import { useAPIv2Result, APIV2Context } from "~/api-v2";
import { useAPIActions } from "@macrostrat/ui-components";

function buildLink(props: { route: string }) {
  const { route } = props;

  return "/api/v2" + route;
}

function unwrapResponse(res) {
  if (res.fields) {
    return res.fields;
  }
}

async function fetchFields(link: string, get) {
  const res = await get(link);

  const data = unwrapResponse(res);

  return data;
}

function unwrapModels(res) {
  if (res.routes) {
    let routes = res.routes;
    let vocab: object = routes.vocabulary;
    let models: object = routes.models;
    let tags: object = routes.tags;

    let total_routes = { ...vocab, ...models, ...tags };

    let namesAndRoutes: object = {};
    Object.keys(total_routes).map(key => {
      let name = key.split("/").slice(-1)[0];
      let route = key;
      namesAndRoutes = { ...namesAndRoutes, ...{ [name]: route } };
    });
    return namesAndRoutes;
  }
}

async function getPossibleModels(get) {
  const url: string = "/api/v2";
  const data = await get(url);

  return unwrapModels(data);
}

/**
 * Function to dynamically index a dictionary with multiple nests
 * @param dict Dictionary to index
 * @param list List of keys to index down to
 */
function dynamicDictIndexer(dict: object, list: []) {
  let listCopy = [...list];
  if (listCopy.length == 0) {
    // finished recursion
  }

  let newDict = dict[listCopy[0]];
  delete listCopy[0];
}

//obj[list[1]][list[2]] = fields;

export { fetchFields, getPossibleModels };
