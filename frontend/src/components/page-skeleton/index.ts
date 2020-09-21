import { hyperStyled } from "@macrostrat/hyper";
import { PageFooter } from "app/shared/footer";
import { CatalogNavLinks } from "app/admin";
import { AppNavbar, NavButton } from "./navbar";
import { PropsWithChildren } from "react";
import { Route } from "react-router-dom";
import styles from "./module.styl";

const h = hyperStyled(styles);

enum PageStyle {
  BASIC = "basic",
  WIDE = "wide",
  // Fullscreen pages are responsible for managing their own navigation
  FULLSCREEN = "fullscreen",
}

const MainNavbar = (props) =>
  h(AppNavbar, { ...props, fullTitle: true }, [
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
      h.if(showNavbar)(MainNavbar, { fixedToTop: style == PageStyle.WIDE }),
      // Render component if it exists, otherwise use render function
      h("div.page-content", null, children),
    ]),
    h.if(showFooter)(PageFooter),
  ]);
}

PageSkeleton.defaultProps = { style: PageStyle.BASIC };

function PageRoute(props) {
  /** A custom route to manage page header, footer, and style associated
      with a specific route */
  const { render, component: base, style, ...rest } = props;
  const component = (p) => {
    const children = base != null ? h(base, p) : render(p);
    return h(PageSkeleton, { style, children });
  };
  return h(Route, { ...rest, component });
}

export * from "./navbar";
export { PageSkeleton, PageStyle, PageRoute };
