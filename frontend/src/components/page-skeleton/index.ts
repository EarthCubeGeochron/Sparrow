import { hyperStyled } from "@macrostrat/hyper";
import { PageFooter } from "app/shared/footer";
import { CatalogNavLinks } from "app/admin";
import { AppNavbar, NavButton } from "app/components/navbar";
import styles from "./module.styl";

const h = hyperStyled(styles);

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
  return h("div.page-skeleton", [
    h("div.expander", [
      h.if(!hideNavbar)(MainNavbar),
      // Render component if it exists, otherwise use render function
      children,
    ]),
    h.if(!hideNavbar)(PageFooter),
  ]);
}

PageSkeleton.defaultProps = { hideNavbar: false };

export { PageSkeleton };
