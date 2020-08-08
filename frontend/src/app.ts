/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import h, { C } from "@macrostrat/hyper";
import { useEffect } from "react";
import { join } from "path";
import {
  BrowserRouter as Router,
  Route,
  Switch,
  useLocation,
} from "react-router-dom";
import { HomePage } from "./homepage";

import siteContent from "site-content";
import { FrameProvider } from "./frame";
import { Intent } from "@blueprintjs/core";
import { APIProvider } from "@macrostrat/ui-components";
import { APIExplorer } from "./api-explorer";
import { PageFooter } from "./shared/footer";
import { AuthProvider } from "./auth";
import { AppToaster } from "./toaster";
import { Catalog, CatalogNavLinks } from "./admin";
import { AppNavbar, NavButton } from "./components/navbar";
import { MapPage } from "./map";
import Table from "./table/App";
import styled from "@emotion/styled";
import DataSheet from "./data-sheet/app";

const AppHolder = styled.div`\
display: flex;
flex-direction: column;
min-height: 100vh;\
`;

const Expander = styled.div`\
flex-grow: 1;\
`;

const MainNavbar = (props) =>
  h(AppNavbar, { fullTitle: true }, [
    h(CatalogNavLinks, { base: "/catalog" }),
    h(NavButton, { to: "/map" }, "Map"),
    h(NavButton, { to: "/data-sheet" }, "Data Sheet"),
    h(AppNavbar.Divider),
    h(NavButton, { to: "/api-explorer/v1" }, "API"), // NavButton, similar to React-Router 'Link' takes the 'to' arg
  ]);

function PageSkeleton(props) {
  const { hideNavbar, children } = props;
  return h(AppHolder, [
    h(Expander, [
      h.if(!hideNavbar)(MainNavbar),
      // Render component if it exists, otherwise use render function
      children,
    ]),
    h.if(!hideNavbar)(PageFooter),
  ]);
}

PageSkeleton.defaultProps = { hideNavbar: false };

function PageRoute(props) {
  /** A custom route to manage page header, footer, and style associated
      with a specific route */
  const { render, component: base, hideNavbar, ...rest } = props;
  const children = base != null ? h(base) : render();
  const component = () => h(PageSkeleton, { hideNavbar, children });
  return h(Route, { ...rest, component });
}

function AppMain(props) {
  // Handles routing for the application between pages
  const { baseURL } = props;

  // Tab Title becomes WiscAr-Sparrow
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
        path: "/map",
        hideNavbar: true,
        component: MapPage,
      }),
      h(PageRoute, {
        path: "/data-sheet",
        component: DataSheet,
      }),
      h(PageRoute, { path: "/api-explorer", component: APIExplorer }),
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

const App = function () {
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
