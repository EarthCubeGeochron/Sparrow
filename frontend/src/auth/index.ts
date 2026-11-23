import { hyperStyled } from "@macrostrat/hyper";
import { Button, IconName } from "@blueprintjs/core";
import { LoginForm } from "./login-form";
import { AuthProvider, useAuth } from "./context";
import styles from "./module.styl";
const h = hyperStyled(styles);

function AuthStatus(props) {
  const { runAction, username } = useAuth();
  let { className, large = true } = props;

  let text = "Not logged in";
  let icon: IconName = "blocked-person";
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
        onClick: () => runAction({ type: "request-form" }),
      },
      text
    ),
  ]);
}

export * from "./login-form";
export * from "./util";
export { AuthProvider, AuthStatus, useAuth };
