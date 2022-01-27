import h, { C, compose } from "@macrostrat/hyper";
import { useEffect } from "react";
import { join } from "path";
import { BrowserRouter as Router, Switch } from "react-router-dom";
import loadable from "@loadable/component";
import siteContent from "site-content";
import { FrameProvider } from "./frame";
import { Intent } from "@blueprintjs/core";
import { DarkModeManager, PageRoute, NoMatchPage } from "~/util";
import { APIProvider } from "@macrostrat/ui-components";
import { APIExplorer } from "./api-explorer";
import { AuthProvider } from "./auth";
import { AppToaster } from "./toaster";
import { AdminRoute } from "./admin";
import SchemaExplorerMainPanel from "./schema-explorer";
import { PageStyle } from "~/components/page-skeleton";
import HomePage from "./homepage";
import Catalog from "./catalog";
import { Frame } from "./frame";

//import { MapSelector } from "./data-sheet/sheet-enter-components";

const APIExplorerV2 = loadable(async function () {
  const module = await import("./api-v2");
  return module.APIExplorerV2;
});

const MapPage = loadable(async function () {
  const module = await import("./map");
  return module.MapPage;
});

function AppRouter(props) {
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
        render: () => h(Catalog, { base: "/catalog" }),
      }),
      h(PageRoute, {
        path: "/map",
        style: PageStyle.FULLSCREEN,
        component: MapPage,
      }),
      h(AdminRoute, { path: "/admin" }),
      h(PageRoute, { path: "/api-explorer", component: APIExplorer }),
      h(PageRoute, {
        path: "/api-explorer/v2",
        component: APIExplorerV2,
        exact: true,
      }),
      h(PageRoute, {
        path: "/import-schema-explorer",
        component: SchemaExplorerMainPanel,
      }),
      h(Frame, { id: "extraPages", default: null }, null),
      h(PageRoute, { path: "*", component: NoMatchPage }),
    ])
  );
}

const errorHandler = function (route, response) {
  let msg;
  const { error } = response;
  if (error != null) {
    msg = error.message;
  }
  const message = h("div.api-error", [h("code.bp3-code", route), h("p", msg)]);
  return AppToaster.show({ message, intent: Intent.DANGER });
};

function App() {
  // Nest application in React context providers
  const baseURL = process.env.BASE_URL ?? "/";
  const apiBaseURL = join(process.env.BASE_URL ?? "/", "/api/v1"); //process.env.BASE_URL || "/";

  return h(
    compose(
      C(FrameProvider, { overrides: siteContent }),
      C(APIProvider, { baseURL: apiBaseURL, onError: errorHandler }),
      AuthProvider,
      DarkModeManager,
      C(AppRouter, { baseURL })
    )
  );
}

export default App;
