/*
The catalog is the public-facing data display for Sparrow.
It shares many attributes with the /admin section, but does
not include editing functionality.
*/
import { hyperStyled } from "@macrostrat/hyper";
import { Switch } from "react-router-dom";
import { Frame } from "~/frame";
import { ErrorBoundaryRoute as Route } from "~/util";
import { DataModelLinks } from "./nav";
import { SessionListComponent } from "./session-list";
import { ProjectListComponent } from "./project-list";
import { ProjectMatch } from "~/model-views/project";
import { SampleMain } from "~/model-views/sample";
import { LoginSuggest } from "~/auth";
import { InsetText } from "~/components/layout";
import { CatalogNavbar } from "./nav";
//@ts-ignore
import styles from "./module.styl";
import { SessionMatch } from "../model-views/session";
import { DataFilesMain } from "../model-views/data-files";
import { APIProvider } from "@macrostrat/ui-components";
import { APIV3Context } from "~/api-v2";

const h = hyperStyled(styles);

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
    h(Route, {
      path: base + "/data-file",
      // style: PageStyle.WIDE,
      component: DataFilesMain,
    }),
    h(Route, {
      path: base,
      component: CatalogMain,
      exact: true,
    }),
  ]);

const Catalog = ({ base }) =>
  h(APIProvider, { baseURL: "/api/v3/" }, [
    h("div.catalog", [
      h(CatalogNavbar, { base }),
      h(LoginSuggest),
      h(CatalogBody, { base }),
    ]),
  ]);

export default Catalog;
