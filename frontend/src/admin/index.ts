import { hyperStyled } from "@macrostrat/hyper";
import { useContext } from "react";
import { Switch } from "react-router-dom";
import loadable from "@loadable/component";
import { LinkCard } from "@macrostrat/ui-components";

import { Frame } from "~/frame";
import { LoginRequired } from "~/auth";
import { ErrorBoundaryRoute as Route, NoMatchPage } from "~/util";
import { AuthContext } from "~/auth/context";
import { ProjectAdminPage } from "./project";

import { SampleAdminPage } from "./sample";
import { PageRoute, PageStyle, AppNavbar } from "~/components/page-skeleton";
import { NavButton } from "~/components";
import styles from "./module.styl";
import { SessionAdminPage } from "./session";
import { DataFileAdminPage } from "./data-file";
import { VocabularyPage } from "./vocabulary";

import { NewProjectForm } from "../model-views/project/new-project";
import { NewSamplePage } from "~/model-views/sample/new-sample";

const DataSheet = loadable(() => import("./data-sheet"));

const h = hyperStyled(styles);

function AdminDataModelLinks(props) {
  const { base = "/catalog" } = props;
  return h("div.data-model-links", [
    h(LinkCard, { to: base + "/project" }, h("h2", "Projects")),
    h(LinkCard, { to: base + "/sample" }, h("h2", "Samples")),
    h(LinkCard, { to: base + "/session" }, h("h2", "Sessions")),
    h(LinkCard, { to: base + "/data-file" }, h("h2", "Data files")),
  ]);
}

const AdminNavLinks = function ({ base }) {
  if (base == null) {
    base = "/catalog";
  }
  return h("div", [
    h(NavButton, { to: base + "/project" }, "Projects"),
    h(NavButton, { to: base + "/sample" }, "Samples"),
    h(NavButton, { to: base + "/session" }, "Sessions"),
    h(NavButton, { to: base + "/data-file" }, "Data Files"),
  ]);
};

const AdminNavbar = (props) => {
  const { base, ...rest } = props;
  return h(AppNavbar, { ...rest, fullTitle: true, subtitle: "Admin" }, [
    h(AdminNavLinks, { base }),
    h(AppNavbar.Divider),
    h(NavButton, { to: base + "/data-sheet" }, "Metadata"),
    h(NavButton, { to: "/map" }, "Map"),
    h(
      NavButton,
      { to: base + "/terms/parameter", icon: "data-lineage" },
      "Terms"
    ),
  ]);
};

const AdminBody = ({ base, ...rest }) => {
  return h(Frame, { id: "adminBase", ...rest }, [
    h(AdminDataModelLinks, { base }),
  ]);
};

const AdminRouter = ({ base }) =>
  h(Switch, [
    h(Route, {
      path: base + "/data-sheet",
      render: () => h(DataSheet),
    }),
    h(Route, {
      path: base + "/session",
      render: () => h(SessionAdminPage),
    }),
    h(Route, {
      path: base + "/project",
      render: () => h(ProjectAdminPage),
    }),
    h(Route, {
      path: base + "/new-project",
      render: () => h(NewProjectForm),
    }),
    h(Route, {
      path: base + "/new-sample",
      render: () => h(NewSamplePage),
    }),
    h(Route, {
      path: base + "/sample",
      render: () => h(SampleAdminPage),
    }),
    h(Route, {
      path: base + "/terms",
      render: () => h(VocabularyPage),
    }),
    h(PageRoute, {
      path: base + "/data-file",
      style: PageStyle.WIDE,
      render: () => h(DataFileAdminPage),
    }),
    h(Route, {
      path: base,
      render: () => h(AdminBody, { base }),
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
  /* Base route for the admin section of the website */
  const base = "/admin";
  return h(PageRoute, {
    path,
    style: PageStyle.WIDE,
    navComponent: () => h(AdminNavbar, { base }),
    render: () => h(AdminPage, { base }),
  });
}

export { AdminPage, AdminRoute };
