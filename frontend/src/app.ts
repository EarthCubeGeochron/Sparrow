/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import h from "@macrostrat/hyper";
import { useEffect } from "react";
import { join } from "path";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import { HomePage } from "./homepage";

import siteContent from "site-content";
import { FrameProvider } from "./frame";
import { Intent } from "@blueprintjs/core";
import { APIProvider } from "@macrostrat/ui-components";
import { APIExplorer } from "./api-explorer";
import { APIExplorerV2 } from "./api-v2";
import { AuthProvider } from "./auth";
import { AppToaster } from "./toaster";
import { Catalog } from "./admin";
import { PageSkeleton, PageStyle } from "./components/page-skeleton";
import { MapPage } from "./map";
import NewSample from "./new-sample/new-sample";

import DataSheet from "./data-sheet/app";

function PageRoute(props) {
  /** A custom route to manage page header, footer, and style associated
      with a specific route */
  const { render, component: base, style, ...rest } = props;
  const component = (p) => {
    const children = base != null ? h(base, p) : render(p);
    return h(PageSkeleton, { style, children });
  };
  return h(Route, { ...rest, component });
}

function AppMain(props) {
  // Handles routing for the application between pages
  const { baseURL } = props;

  // Tab Title becomes WiscAr-Sparrow
  // TODO: We could use the 'react-helmet' library to manage this...
  useEffect(() => {
    const labname = process.env.SPARROW_LAB_NAME;
    document.title = labname != null ? `${labname} – Sparrow` : "Sparrow";
  }, []);

  return h(
    Router,
    { basename: baseURL },
    h(Switch, [
      h(PageRoute, {
        path: "/",
        exact: true,
        component: HomePage,
      }),
      h(PageRoute, {
        path: "/catalog",
        render() {
          return h(Catalog, { base: "/catalog" });
        },
      }),
      h(PageRoute, {
        path: "/new-sample",
        style: PageStyle.WIDE,
        component: NewSample,
      }),
      h(PageRoute, {
        path: "/map",
        style: PageStyle.FULLSCREEN,
        component: MapPage,
      }),
      h(PageRoute, {
        path: "/data-sheet",
        style: PageStyle.WIDE,
        component: DataSheet,
      }),
      h(PageRoute, {
        path: "/api-explorer",
        component: APIExplorerV2,
        exact: true,
      }),
      h(PageRoute, { path: "/api-explorer-v1", component: APIExplorer }),
    ])
  );
}

const errorHandler = function(route, response) {
  let msg;
  const { error } = response;
  if (error != null) {
    msg = error.message;
  }
  const message = h("div.api-error", [h("code.bp3-code", route), h("p", msg)]);
  return AppToaster.show({ message, intent: Intent.DANGER });
};

const App = function() {
  // Nest application in React context providers
  const baseURL = process.env.BASE_URL || "/";
  const apiBaseURL = join(baseURL, "/api/v1");
  console.log(apiBaseURL);

  return h(
    FrameProvider,
    { overrides: siteContent },
    h(
      APIProvider,
      { baseURL: apiBaseURL, onError: errorHandler },
      h(AuthProvider, null, h(AppMain, { baseURL }))
    )
  );
};

export { App };
