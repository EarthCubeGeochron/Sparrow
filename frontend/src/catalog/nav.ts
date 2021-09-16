import { hyperStyled } from "@macrostrat/hyper";
import { LinkCard } from "@macrostrat/ui-components/src/ext/router-links";
import { NavButton } from "~/components";
import styles from "./module.styl";

const h = hyperStyled(styles);

const CatalogNavLinks = function ({ base }) {
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

function DataModelLinks(props) {
  const { base = "/catalog" } = props;
  return h("div.data-model-links", [
    h(LinkCard, { to: base + "/project" }, h("h2", "Projects")),
    h(LinkCard, { to: base + "/sample" }, h("h2", "Samples")),
    h(LinkCard, { to: base + "/session" }, h("h2", "Sessions")),
    h(LinkCard, { to: base + "/data-file" }, h("h2", "Data files")),
  ]);
}

const CatalogNavbar = (
  { base, ...rest } // A standalone navbar for the admin panel, can be enabled by default
) =>
  h("div.minimal-navbar", { ...rest, subtitle: "Admin" }, [
    h(
      NavButton,
      { to: base, exact: true, active: false },
      h("h4", "Data Catalog")
    ),
    h(CatalogNavLinks, { base }),
  ]);

export { CatalogNavLinks, CatalogNavbar, DataModelLinks };
