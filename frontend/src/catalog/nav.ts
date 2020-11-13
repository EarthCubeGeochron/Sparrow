import { hyperStyled } from "@macrostrat/hyper";
import { NavButton } from "~/components";
import styles from "./module.styl";

const h = hyperStyled(styles);

const CatalogNavLinks = function ({ base, ...rest }) {
  if (base == null) {
    base = "/catalog";
  }
  return h([
    h(NavButton, { to: base + "/project" }, "Projects"),
    h(NavButton, { to: base + "/sample" }, "Samples"),
    h(NavButton, { to: base + "/session" }, "Sessions"),
    h(NavButton, { to: base + "/data-file" }, "Data Files"),
  ]);
};

const AdminNavLinks = function ({ base, ...rest }) {
  if (base == null) {
    base = "/catalog";
  }
  return h([
    h(NavButton, { to: base + "/project" }, "Projects"),
    h(NavButton, { to: base + "/sample" }, "Samples"),
    h(NavButton, { to: base + "/session" }, "Sessions"),
    h(NavButton, { to: base + "/data-file" }, "Data Files"),
  ]);
};

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

export { CatalogNavLinks, CatalogNavbar, AdminNavLinks };
