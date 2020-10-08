import { hyperStyled } from "@macrostrat/hyper";
import { useContext } from "react";
import { Switch } from "react-router-dom";
import loadable from "@loadable/component";

import { Frame } from "~/frame";
import { LoginRequired } from "~/auth";
import { ErrorBoundaryRoute as Route, NoMatchPage } from "~/util";
import { AuthContext } from "~/auth/context";
import { ProjectAdminPage } from "./project";
import { SampleMain } from "~/model-views/sample";
import { DataFilesPage } from "./data-file";
import { PageRoute, PageStyle, AppNavbar } from "~/components/page-skeleton";
import { DataModelLinks } from "~/catalog";
import { NavButton } from "~/components";
import { CatalogNavLinks } from "~/catalog/nav";
import styles from "./module.styl";

const DataSheet = loadable(() => import("./data-sheet"));

const h = hyperStyled(styles);

const AdminNavbar = (props) => {
  const { base, ...rest } = props;
  return h(AppNavbar, { ...rest, fullTitle: true, subtitle: "Admin" }, [
    h(CatalogNavLinks, { base }),
    h(AppNavbar.Divider),
    h(NavButton, { to: base + "/data-sheet" }, "Sheet"),
    h(NavButton, { to: "/map" }, "Map"),
    h(NavButton, { to: base + "/lexicon" }, "Lexicon"),
  ]);
};

const AdminBody = ({ base, ...rest }) => {
  return h(Frame, { id: "adminBase", ...rest }, [h(DataModelLinks, { base })]);
};

const AdminRouter = ({ base }) =>
  h(Switch, [
    h(Route, {
      path: base + "/data-sheet",
      component: DataSheet,
    }),
    h(Route, {
      path: base + "/session",
      component: "div",
    }),
    h(Route, {
      path: base + "/project",
      component: () => h(ProjectAdminPage),
    }),
    h(Route, {
      path: base + "/sample",
      component: SampleMain,
    }),
    h(PageRoute, {
      path: base + "/data-file",
      style: PageStyle.WIDE,
      component: DataFilesPage,
    }),
    h(Route, {
      path: base,
      component: () => h(AdminBody, { base }),
      exact: true,
    }),
    h(Route, { path: "*", component: NoMatchPage }),
  ]);

function AdminPage(props) {
  const { base } = props;
  const { login, requestLoginForm } = useContext(AuthContext);
  if (!login) {
    return h(LoginRequired, { requestLoginForm });
  }
  return h(AdminRouter, { base });
}

function AdminRoute({ path }) {
  const base = "/admin";
  return h(PageRoute, {
    path,
    style: PageStyle.WIDE,
    navComponent: () => h(AdminNavbar, { base }),
    component: () => h(AdminPage, { base }),
  });
}

export { AdminPage, AdminRoute };
