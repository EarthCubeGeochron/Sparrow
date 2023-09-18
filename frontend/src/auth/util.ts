import { hyperStyled } from "@macrostrat/hyper";
import { NonIdealState, Button, Callout } from "@blueprintjs/core";

import { useAuth } from "./context";
import styles from "./main.module.styl";

const h = hyperStyled(styles);

const LoginButton = function (props) {
  const { runAction } = useAuth();
  return h(
    Button,
    {
      onClick() {
        runAction({ type: "request-form", enabled: true });
      },
      className: "login-button",
      ...props,
    },
    "Login"
  );
};

const LoginRequired = function (props) {
  return h(NonIdealState, {
    title: "Not logged in",
    description:
      "You must be authenticated to use the administration interface.",
    icon: "blocked-person",
    action: h(LoginButton),
    ...props,
  });
};

const LoginSuggest = function () {
  const { login } = useAuth();
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

export { LoginButton, LoginRequired, LoginSuggest };
