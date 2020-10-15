/*
The catalog is the public-facing data display for Sparrow.
It shares many attributes with the /admin section, but does
not include editing functionality.
*/
import { hyperStyled } from "@macrostrat/hyper";
import { Switch } from "react-router-dom";
import { LinkCard } from "@macrostrat/ui-components";
import { Frame } from "~/frame";
import { ErrorBoundaryRoute as Route } from "~/util";
import { SessionListComponent } from "./session-list";
import { ProjectListComponent } from "./project-list";
import { ProjectMatch } from "~/model-views/project";
import { SampleMain } from "~/model-views/sample";
import { DataFilesMain } from "~/model-views/data-files";
import { PageRoute, PageStyle } from "~/components/page-skeleton";
import { LoginSuggest } from "~/auth";
import { InsetText } from "~/components/layout";
import { CatalogNavbar } from "./nav";
import styles from "./module.styl";
import { SessionMatch } from "../model-views/session";

const h = hyperStyled(styles);

// const SessionMatch = function({ match }) {
//   const { id } = match.params;
//   return h(SessionComponent, { id });
// };

function DataModelLinks(props) {
  const { base = "/catalog" } = props;
  return h("div.data-model-links", [
    h(LinkCard, { to: base + "/project" }, h("h2", "Projects")),
    h(LinkCard, { to: base + "/sample" }, h("h2", "Samples")),
    h(LinkCard, { to: base + "/session" }, h("h2", "Sessions")),
    // h(LinkCard, { to: base + "/data-file" }, h("h2", "Data files")),
  ]);
}

function AdminDataModelLinks(props) {
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
  return h(Frame, { id: "catalogBase", ...rest }, [
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
      component: DataFilesMain,
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

export { Catalog, AdminDataModelLinks, DataModelLinks };
