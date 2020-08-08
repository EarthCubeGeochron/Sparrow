/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS206: Consider reworking classes to avoid initClass
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import { hyperStyled } from "@macrostrat/hyper";
import { Component, useContext } from "react";
import {
  NonIdealState,
  Intent,
  Button,
  ButtonGroup,
  Icon,
  Callout,
} from "@blueprintjs/core";
import { Switch } from "react-router-dom";
import { ErrorBoundaryRoute as Route } from "app/util/route";
import T from "prop-types";

import { LinkButton, LinkCard } from "@macrostrat/ui-components";
import { Frame } from "app/frame";
import { AuthContext } from "app/auth/context";
import { ProjectListComponent, ProjectComponent } from "./project";
import { SessionListComponent } from "./session-list-component";
import { SessionComponent } from "./session-component";
import { SampleMain } from "./sample";

import { NavButton } from "app/components";
import { InsetText } from "app/components/layout";
import styles from "./module.styl";

const h = hyperStyled(styles);

const HomeButton = (props) =>
  h(LinkButton, {
    className: "home-link-button",
    icon: "home",
    minimal: true,
    ...props,
  });

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
    h("h4", "Admin"),
    h(HomeButton, { to: base, exact: true }),
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

const LoginButton = function (props) {
  const { requestLoginForm: onClick } = useContext(AuthContext);
  return h(Button, { onClick, className: "login-button", ...props }, "Login");
};

const LoginRequired = function (props) {
  const { requestLoginForm: onClick, ...rest } = props;
  return h(NonIdealState, {
    title: "Not logged in",
    description:
      "You must be authenticated to use the administration interface.",
    icon: "blocked-person",
    action: h(LoginButton),
    ...rest,
  });
};

const LoginSuggest = function () {
  const { login, requestLoginForm } = useContext(AuthContext);
  if (login) {
    return null;
  }
  return h(
    Callout,
    {
      title: "Not logged in",
      icon: "blocked-person",
      intent: "warning",
      className: "login-callout",
    },
    [
      h("p", "Embargoed data and management tools are hidden."),
      h(LoginButton, { intent: "warning", minimal: true }),
    ]
  );
};

const AdminMain = (props) =>
  h(Frame, { id: "adminBase", ...props }, [
    h("h1", "Catalog"),
    h("div.catalog-index", [
      h(
        InsetText,
        "The lab's data catalog can be browsed using several entrypoints:"
      ),
      h(LinkCard, { to: "/project" }, h("h2", "Projects")),
      h(LinkCard, { to: "/sample" }, h("h2", "Samples")),
      h(LinkCard, { to: "/session" }, h("h2", "Sessions")),
    ]),
  ]);

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
      path: base,
      component: AdminMain,
      exact: true,
    }),
  ]);

const Catalog = ({ base }) =>
  h("div.catalog", [h(LoginSuggest), h(CatalogBody, { base })]);

class Admin extends Component {
  static initClass() {
    // A login-required version of the catalog
    this.contextType = AuthContext;
    this.propTypes = {
      base: T.string.isRequired,
    };
  }
  render() {
    const { base } = this.props;
    const { login, requestLoginForm } = this.context;
    if (!login) {
      return h(LoginRequired, { requestLoginForm });
    }

    return h("div.admin", [h(CatalogBody, { base })]);
  }
}
Admin.initClass();

export { Catalog, CatalogNavLinks };
