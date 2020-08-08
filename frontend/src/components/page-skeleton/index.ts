import { hyperStyled } from "@macrostrat/hyper";
import { PageFooter } from "app/shared/footer";
import { CatalogNavLinks } from "app/admin";
import { AppNavbar, NavButton } from "app/components/navbar";
import { PropsWithChildren } from "react";
import styles from "./module.styl";

const h = hyperStyled(styles);

enum PageStyle {
  BASIC = "basic",
  WIDE = "wide",
  // Fullscreen pages are responsible for managing their own navigation
  FULLSCREEN = "fullscreen",
}

const MainNavbar = (props) =>
  h(AppNavbar, { fullTitle: true }, [
    h(CatalogNavLinks, { base: "/catalog" }),
    h(NavButton, { to: "/map" }, "Map"),
    h(NavButton, { to: "/data-sheet" }, "Data Sheet"),
    h(AppNavbar.Divider),
    h(NavButton, { to: "/api-explorer/v1" }, "API"), // NavButton, similar to React-Router 'Link' takes the 'to' arg
  ]);

type PageSkeletonProps = PropsWithChildren<{
  style: PageStyle;
}>;

function PageSkeleton(props: PageSkeletonProps) {
  /** A basic page skeleton */
  const { style, children } = props;

  const showNavbar = style != PageStyle.FULLSCREEN;
  const showFooter = style == PageStyle.BASIC;

  return h("div.page-skeleton", { className: style }, [
    h("div.expander", [
      h.if(showNavbar)(MainNavbar),
      // Render component if it exists, otherwise use render function
      children,
    ]),
    h.if(showFooter)(PageFooter),
  ]);
}

PageSkeleton.defaultProps = { style: PageStyle.BASIC };

export { PageSkeleton, PageStyle };
