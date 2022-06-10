import { hyperStyled } from "@macrostrat/hyper";
import { useContext } from "react";
import { Switch, Link } from "react-router-dom";
import loadable from "@loadable/component";
import { LinkCard } from "@macrostrat/ui-components";
import { Spinner, MenuItem, Menu, Divider } from "@blueprintjs/core";

import { Frame } from "~/frame";
import { LoginRequired } from "~/auth";
import { ErrorBoundaryRoute as Route, NoMatchPage } from "~/util";
import { AuthContext } from "~/auth/context";
import { ProjectAdminPage } from "./project";
import { OpenSearch } from "~/components";

import { SampleAdminPage } from "./sample";
import { PageRoute, PageStyle, AppNavbar } from "~/components/page-skeleton";
import { NavButton } from "~/components";
import { SessionAdminPage } from "./session";
import { DataFileAdminPage } from "./data-file";
import { VocabularyPage } from "./vocabulary";

import { TagManager } from "~/components/tags";

//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

const DataSheetPage = loadable(() => import("./data-sheet"), {
  fallback: h(Spinner),
});

const TasksPage = loadable(() => import("./tasks"), {
  fallback: h(Spinner),
});

function AdminDataModelLinks(props) {
  const { base = "/catalog" } = props;
  return h("div.data-model-links", [
    h(LinkCard, { to: base + "/project" }, h("h2", "Projects")),
    h(LinkCard, { to: base + "/sample" }, h("h2", "Samples")),
    h(LinkCard, { to: base + "/session" }, h("h2", "Sessions")),
    h(LinkCard, { to: base + "/data-file" }, h("h2", "Data files")),
  ]);
}

function SecondaryMenuItem(props) {
  const { icon = null, to, children } = props;
  return h(MenuItem, { icon, text: h(Link, { to }, children) });
}

function SecondaryPageLinks(props) {
  const { base = "/admin" } = props;
  return h(Menu, [
    h(SecondaryMenuItem, { to: base + "/tasks" }, "Tasks"),
    h(SecondaryMenuItem, { to: base + "/data-sheet" }, "Metadata"),
    h(SecondaryMenuItem, { to: base + "/terms/parameter" }, "Terms"),
    h(SecondaryMenuItem, { to: "/map" }, "Map"),
  ]);
}

function NewModelLinks(props) {
  const { base = "/admin" } = props;
  return h(Menu, [
    h(SecondaryMenuItem, { to: base + "/tag-manager" }, "Tag Manager"),
  ]);
}

const AdminNavbarLinks = function ({ base }) {
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
  return h(
    AppNavbar,
    {
      ...rest,
      fullTitle: true,
      subtitle: h(Link, { to: base }, "Admin"),
    },
    [
      h(AdminNavbarLinks, { base }),
      h(AppNavbar.Divider),
      h(NavButton, { to: base + "/data-sheet" }, "Metadata"),
      h(NavButton, { to: "/map" }, "Map"),
      h(
        NavButton,
        { to: base + "/terms/parameter", icon: "data-lineage" },
        "Terms"
      ),
    ]
  );
};

const QuickLinks = ({ base }) => {
  return h("div", { style: { position: "sticky", top: "0px" } }, [
    h(QuickHeader, { text: "Quick Links" }),
    h(AdminDataModelLinks, { base }),
  ]);
};

const QuickHeader = (props) => {
  const { text } = props;

  return h(
    "div",
    { style: { marginBottom: "20px", position: "sticky", top: "0px" } },
    [
      h("h2", { style: { marginTop: "0px", marginBottom: "0px" } }, text),
      h(Divider),
    ]
  );
};

const AdminBody = ({ base, ...rest }) => {
  return h(Frame, { id: "adminBase", ...rest }, [
    h(
      "div.admin-homepage",
      { style: { display: "flex", justifyContent: "space-between" } },
      [
        h("div", { style: { flexGrow: 2 } }, [
          h(QuickLinks, { base }),
          h("div", { style: { display: "flex" } }, [
            h(SecondaryPageLinks, { base }),
            h(NewModelLinks, { base }),
          ]),
        ]),
        h(
          "div",
          {
            style: {
              flexGrow: 1,
              marginRight: "50px",
              width: "28em",
              marginLeft: "15px",
            },
          },
          [h(QuickHeader, { text: "Quick Search" }), h(OpenSearch)]
        ),
      ]
    ),
  ]);
};

const AdminRouter = ({ base }) =>
  h(Switch, [
    h(Route, {
      path: base + "/data-sheet",
      render: () => h(DataSheetPage),
    }),
    h(Route, {
      path: base + "/tasks",
      render: () => h(TasksPage),
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
      path: base + "/sample",
      render: () => h(SampleAdminPage),
    }),
    h(Route, {
      path: base + "/tag-manager",
      render: () => h(TagManager),
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
