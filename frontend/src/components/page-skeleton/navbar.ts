import { hyperStyled, classed, addClassNames } from "@macrostrat/hyper";
import { Navbar } from "@blueprintjs/core";
import { NavLink } from "react-router-dom";
import { NavLinkButton, DarkModeButton } from "@macrostrat/ui-components";

import { AuthStatus } from "app/auth";
import { Frame } from "app/frame";
import styles from "./module.styl";

const h = hyperStyled(styles);

const NavButton = classed(NavLinkButton, styles["navbar-button"]);

const SiteTitle = () =>
  h(NavLink, { to: "/" }, h(Frame, { id: "siteTitle" }, "Test Lab"));

function AppNavbar({ children, fullTitle, subtitle, ...rest }) {
  const p = addClassNames(rest, "app-navbar");
  return h(Navbar, p, [
    h(Navbar.Group, [
      h(Navbar.Heading, [
        h("h1.site-title", null, [
          h(SiteTitle),
          h.if(subtitle != null)([
            h("span", " "),
            h("span.subtitle", subtitle),
          ]),
        ]),
      ]),
      h.if(children != null)(Navbar.Divider),
      children,
    ]),
    h("div.navbar-spacer"),
    h(Navbar.Group, [
      h(DarkModeButton, { minimal: true, active: false }),
      h(AuthStatus, { className: "auth-right" }),
    ]),
  ]);
}

AppNavbar.Divider = Navbar.Divider;

const MinimalNavbar = (props) => h("div.minimal-navbar", props);

export { AppNavbar, NavButton, SiteTitle, MinimalNavbar };
