import h from "@macrostrat/hyper";
import loadable from "@loadable/component";

const APIExplorerV3 = loadable(async function () {
  const module = await import("./v3");
  return module.APIExplorerV3;
});

const APIExplorer = function () {
  return h("div#api", [h(APIExplorerV3)]);
};

export { APIExplorer };
