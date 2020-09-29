import { hyperStyled } from "@macrostrat/hyper";
import { useContext } from "react";
import { Button } from "@blueprintjs/core";
import { LoginForm } from "./login-form";
import { AuthProvider, AuthContext, useAuth } from "./context";
import styles from "./module.styl";
const h = hyperStyled(styles);

function AuthStatus(props) {
  const { requestLoginForm, username } = useContext(AuthContext);
  let { className, large, ...rest } = props;
  if (large == null) {
    large = true;
  }

  let text = "Not logged in";
  let icon = "blocked-person";
  if (username != null) {
    text = username;
    icon = "person";
  }
  return h("div.auth-status", { className }, [
    h(LoginForm),
    h(
      Button,
      {
        minimal: true,
        large,
        icon,
        onClick: requestLoginForm,
      },
      text
    ),
  ]);
}

export * from "./login-form";
export * from "./util";
export { AuthProvider, AuthStatus, useAuth };
