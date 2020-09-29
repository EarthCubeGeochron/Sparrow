import { hyperStyled } from "@macrostrat/hyper";
import { Switch } from "react-router-dom";
import { LinkCard } from "@macrostrat/ui-components";
import { Frame } from "~/frame";
import { ErrorBoundaryRoute as Route } from "~/util/route";
import { ProjectListComponent, ProjectComponent } from "~/admin/project";
import { SessionListComponent } from "./session-list";
import { SessionComponent } from "~/admin/session-component";
import { SampleMain } from "~/admin/sample";
import { DataFilesPage } from "~/admin/data-files";
import { PageRoute, PageStyle } from "~/components/page-skeleton";
import { LoginSuggest } from "~/auth";
import { NavButton } from "~/components";
import { InsetText } from "~/components/layout";
import styles from "~/admin/module.styl";

const h = hyperStyled(styles);

const CatalogNavLinks = function ({ base, ...rest }) {
  if (base == null) {
    base = "/catalog";
  }
  return h([
    h(NavButton, { to: base + "/project" }, "Projects"),
    h(NavButton, { to: base + "/sample" }, "Samples"),
    h(NavButton, { to: base + "/session" }, "Sessions"),
  ]);
};

const CatalogNavbar = (
  { base, ...rest } // A standalone navbar for the admin panel, can be enabled by default
) =>
  h("div.minimal-navbar", { ...rest, subtitle: "Admin" }, [
    h(NavButton, { to: base, exact: true }, h("h4", "Data Catalog")),
    h(CatalogNavLinks, { base }),
  ]);

const SessionMatch = function ({ match }) {
  const { id } = match.params;
  return h(SessionComponent, { id });
};

const ProjectMatch = function ({ match }) {
  const { id } = match.params;
  return h(ProjectComponent, { id });
};

function DataModelLinks(props) {
  const { base = "/catalog" } = props;
  return h("div.data-model-links", [
    h(LinkCard, { to: base + "/project" }, h("h2", "Projects")),
    h(LinkCard, { to: base + "/sample" }, h("h2", "Samples")),
    h(LinkCard, { to: base + "/session" }, h("h2", "Sessions")),
    h(LinkCard, { to: base + "/data-file" }, h("h2", "Data files")),
  ]);
}

const CatalogMain = ({ base, ...rest }) => {
  if (base == null) {
    base = "/catalog";
  }
  return h(Frame, { id: "adminBase", ...rest }, [
    h("h1", "Catalog"),
    h("div.catalog-index", [
      h(
        InsetText,
        "The lab's data catalog can be browsed using several entrypoints:"
      ),
      h(DataModelLinks, { base: "/catalog" }),
    ]),
  ]);
};

const CatalogBody = (
  { base } // Render main body
) =>
  h(Switch, [
    h(Route, {
      path: base + "/session/:id",
      component: SessionMatch,
    }),
    h(Route, {
      path: base + "/session",
      component: SessionListComponent,
    }),
    h(Route, {
      path: base + "/project/:id",
      component: ProjectMatch,
    }),
    h(Route, {
      path: base + "/project",
      component: ProjectListComponent,
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
      component: CatalogMain,
      exact: true,
    }),
  ]);

const Catalog = ({ base }) =>
  h("div.catalog", [
    h(CatalogNavbar, { base }),
    h(LoginSuggest),
    h(CatalogBody, { base }),
  ]);

export { Catalog, CatalogNavLinks, DataModelLinks };
