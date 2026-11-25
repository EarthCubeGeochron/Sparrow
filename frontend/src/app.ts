import h, { C, compose } from "@macrostrat/hyper";
import { useEffect } from "react";
import { BrowserRouter as Router, Switch } from "react-router-dom";
import loadable from "@loadable/component";
import siteContent from "site-content";
import { FrameProvider } from "./frame";
import { Intent } from "@blueprintjs/core";
import { DarkModeManager, PageRoute, NoMatchPage } from "~/util";
import { APIExplorer } from "./api-explorer";
import { AuthProvider } from "./auth";
import { PostgRESTProvider } from "./api/postgrest";
import { AppToaster } from "./toaster";
import { AdminRoute } from "./admin";
import { PageStyle } from "~/components/page-skeleton";
import HomePage from "./homepage";
import Catalog from "./catalog";
import { Frame } from "./frame";

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
  const message = h("div.api-error", [h("code.bp4-code", route), h("p", msg)]);
  return AppToaster.show({ message, intent: Intent.DANGER });
};

const baseURL = process.env.BASE_URL ?? "/";

// Nest application in React context providers
const CoreAppComponent = compose(
  C(FrameProvider, { overrides: siteContent }),
  AuthProvider,
  C(PostgRESTProvider, { onError: errorHandler }),
  DarkModeManager,
  C(AppRouter, { baseURL })
);

function App() {
  return h([h(CoreAppComponent), h(Canary)]);
}

function Canary() {
  return h(
    "div.__canary",
    { style: { display: "none" } },
    "This element is used to test whether the application rendered properly."
  );
}

export default App;
