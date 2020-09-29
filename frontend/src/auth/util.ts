import { hyperStyled } from "@macrostrat/hyper";
import { useContext } from "react";
import { NonIdealState, Button, Callout } from "@blueprintjs/core";

import { AuthContext } from "./context";
import styles from "./module.styl";

const h = hyperStyled(styles);

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

export { LoginButton, LoginRequired, LoginSuggest };
