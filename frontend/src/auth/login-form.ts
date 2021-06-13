import { hyperStyled } from "@macrostrat/hyper";
import { Component } from "react";
import { StatefulComponent } from "@macrostrat/ui-components";
import { AuthContext } from "./context";
import { Button, Dialog, Callout, Intent, Classes } from "@blueprintjs/core";
import classNames from "classnames";
import styles from "./module.styl";

const h = hyperStyled(styles);

class LoginFormInner extends Component {
  render() {
    const className = classNames(Classes.INPUT, "bp3-large");
    const { data, onChange, submitForm } = this.props;
    const onKeyUp = function (e) {
      if (e.key !== "Enter") {
        return;
      }
      return submitForm();
    };

    return h("form.login-form", [
      h("input", {
        type: "text",
        name: "username",
        value: data.username,
        onChange,
        className,
        onKeyUp,
        placeholder: "Username",
      }),
      h("input", {
        type: "password",
        name: "password",
        value: data.password,
        onChange,
        className,
        onKeyUp,
        placeholder: "Password",
      }),
    ]);
  }
}

const defaultState = { data: { username: "", password: "" } };

class LoginForm extends StatefulComponent {
  static contextType = AuthContext;
  constructor() {
    super(...arguments);
    this.resetState = this.resetState.bind(this);
    this.isValid = this.isValid.bind(this);
    this.resetState();
    this.state = defaultState;
  }

  resetState() {
    this.setState(defaultState);
  }

  isValid() {
    const { data } = this.state;
    const { username, password } = data;
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

  renderCallout() {
    const { invalidAttempt, login, username } = this.context;
    if (invalidAttempt) {
      return h(
        Callout,
        {
          className: "login-info",
          title: "Invalid credentials",
          intent: Intent.DANGER,
        },
        "Invalid credentials were provided"
      );
    }
  }

  renderLoginForm() {
    const {
      doLogin,
      login,
      isLoggingIn: isOpen,
      requestLoginForm,
    } = this.context;
    const { data } = this.state;

    const submitForm = () => doLogin(data);

    const onChange = (e) => {
      if (e.target == null) {
        return;
      }
      return this.updateState({
        data: { [e.target.name]: { $set: e.target.value } },
      });
    };

    return [
      h("div.login-form-outer", { className: Classes.DIALOG_BODY }, [
        this.renderCallout(),
        h(LoginFormInner, { data, onChange, submitForm }),
      ]),
      h("div", { className: Classes.DIALOG_FOOTER }, [
        h("div", { className: Classes.DIALOG_FOOTER_ACTIONS }, [
          h(
            Button,
            {
              intent: Intent.PRIMARY,
              large: true,
              onClick: submitForm,
              disabled: !this.isValid(),
            },
            "Login"
          ),
        ]),
      ]),
    ];
  }

  renderLogoutForm() {
    const { doLogout, username } = this.context;
    return [
      h("div.login-form-outer", { className: Classes.DIALOG_BODY }, [
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
      ]),
      h("div", { className: Classes.DIALOG_FOOTER }, [
        h("div", { className: Classes.DIALOG_FOOTER_ACTIONS }, [
          h(
            Button,
            {
              large: true,
              onClick: () => doLogout(),
            },
            "Log out"
          ),
        ]),
      ]),
    ];
  }

  render() {
    const {
      doLogin,
      login,
      isLoggingIn: isOpen,
      requestLoginForm,
    } = this.context;
    const { data } = this.state;

    const onChange = (e) => {
      if (e.target == null) {
        return;
      }
      return this.updateState({
        data: { [e.target.name]: { $set: e.target.value } },
      });
    };

    const onClose = () => {
      this.resetState();
      return requestLoginForm(false);
    };

    const title = "Credentials";
    return h(
      Dialog,
      { isOpen, title, onClose, icon: "key" },
      login ? this.renderLogoutForm() : this.renderLoginForm()
    );
  }
}

export { LoginForm };
