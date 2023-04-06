import { Route, Redirect } from "react-router-dom";
import h from "@macrostrat/hyper";
import loadable from "@loadable/component";

const APIExplorerV2 = loadable(async function () {
  const module = await import("./v2");
  return module.APIExplorerV2;
});

const APIExplorer = function (props) {
  const base = "/api-explorer";
  return h("div", [
    h("div#api", [
      h(Route, {
        path: base + `/v2`,
        component: APIExplorerV2,
      }),
      h(Route, {
        path: base,
        exact: true,
        render() {
          return h(Redirect, { to: base + `/v2` });
        },
      }),
    ]),
  ]);
};

export { APIExplorer };
