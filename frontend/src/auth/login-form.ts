import { hyperStyled } from "@macrostrat/hyper";
import React, { useState } from "react";
import { useAuth } from "./context";
import { Button, Dialog, Callout, Intent, Classes } from "@blueprintjs/core";
import { ServerStatus } from "~/components";
import classNames from "classnames";
import styles from "./module.styl";

const h = hyperStyled(styles);

function ErrorPanel() {
  const { error, invalidAttempt } = useAuth();
  if (error == null || !invalidAttempt) return null;

  let title = "Invalid credentials";
  let children = "Invalid credentials were provided";
  if (error.request?.status == 502) {
    title = "Bad response from backend";
    children = "The Sparrow server is not available";
  }
  return h(Callout, {
    className: "login-info",
    title,
    intent: Intent.DANGER,
    children,
  });
}

type LoginFormState = {
  username: string;
  password: string;
};

function isValid({ username, password }: LoginFormState): boolean {
  if (username == null) {
    return false;
  }
  if (password == null) {
    return false;
  }
  if (password.length < 4) {
    return false;
  }
  if (username.length < 4) {
    return false;
  }
  return true;
}

function CredentialsDialog({
  actionButtons,
  children,
}: {
  actionButtons: React.ReactNode;
  children?: React.ReactNode;
}) {
  const { runAction, isLoggingIn: isOpen } = useAuth();
  const title = "Credentials";
  return h(
    Dialog,
    {
      isOpen,
      title,
      onClose() {
        runAction({ type: "request-form", enabled: false });
      },
      icon: "key",
    },
    [
      h("div.login-form-outer", { className: Classes.DIALOG_BODY }, children),
      h("div", { className: Classes.DIALOG_FOOTER }, [
        h("div", { className: Classes.DIALOG_FOOTER_ACTIONS }, actionButtons),
      ]),
    ]
  );
}

function LogoutForm() {
  const { runAction, username } = useAuth();
  const actionButtons = h([
    h(ServerStatus),
    h(
      Button,
      {
        large: true,
        onClick: () => runAction({ type: "logout" }),
      },
      "Log out"
    ),
  ]);
  return h(CredentialsDialog, { actionButtons }, [
    h(
      Callout,
      {
        className: "login-info",
        title: username,
        intent: Intent.SUCCESS,
        icon: "person",
      },
      h("p", ["Logged in as user ", h("em", username)])
    ),
  ]);
}

const defaultState = { username: "", password: "" };

function _LoginForm() {
  const [state, setState] = useState<LoginFormState>(defaultState);
  const { runAction } = useAuth();

  const submitForm = () => runAction({ type: "login", payload: state });

  const onChange = (e) => {
    if (e.target == null) {
      return;
    }
    setState({ ...state, [e.target.name]: e.target.value });
  };

  const actionButtons = h([
    h(ServerStatus),
    h(
      Button,
      {
        intent: Intent.PRIMARY,
        large: true,
        onClick: submitForm,
        disabled: !isValid(state),
      },
      "Login"
    ),
  ]);

  const className = classNames(Classes.INPUT, "bp4-large");
  const onKeyUp = function (e) {};

  return h(CredentialsDialog, { actionButtons }, [
    h(ErrorPanel),
    //h.if(invalidAttempt)(InvalidCredentialsError),
    h("form.login-form", [
      h("input", {
        type: "text",
        name: "username",
        value: state.username,
        onChange,
        className,
        onKeyUp,
        placeholder: "Username",
      }),
      h("input", {
        type: "password",
        name: "password",
        value: state.password,
        onChange,
        className,
        onKeyUp(e) {
          if (e.key !== "Enter") return;
          submitForm();
        },
        placeholder: "Password",
      }),
    ]),
  ]);
}

function LoginForm() {
  const { login } = useAuth();
  return login ? h(LogoutForm) : h(_LoginForm);
}

export { LoginForm };
