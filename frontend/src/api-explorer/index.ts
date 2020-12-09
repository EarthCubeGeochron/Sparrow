/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import "../shared/ui-init";

import React from "react";
import { render } from "react-dom";
import { Route, Link, Redirect } from "react-router-dom";
import h from "react-hyperscript";
import { RouteComponent } from "./route-component";
import loadable from "@loadable/component";

import "./main.styl";

const APIExplorerV2 = loadable(async function () {
  const module = await import("../api-v2");
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
      h(Route, { path: base + `/v1`, component: RouteComponent }),
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
