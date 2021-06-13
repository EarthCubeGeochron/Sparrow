import h from "react-hyperscript";
import { StatefulComponent, APIActions } from "@macrostrat/ui-components";
import { APIV2Context } from "~/api-v2";
import { createContext, useContext } from "react";

interface AuthCtx {
  login: boolean;
  username: string | null;
  isLoggingIn: boolean;
  invalidAttempt: boolean;
}

const AuthContext = createContext<AuthCtx>({
  login: false,
  username: null,
  isLoggingIn: false,
  invalidAttempt: false,
});

class AuthProvider extends StatefulComponent {
  static contextType = APIV2Context;
  constructor(props) {
    super(props);
    this.requestLoginForm = this.requestLoginForm.bind(this);
    this.render = this.render.bind(this);
    this.state = {
      login: false,
      username: null,
      isLoggingIn: false,
      invalidAttempt: false,
    };
  }

  componentDidMount() {
    return this.getStatus();
  }

  getStatus = async () => {
    // Right now, we get login status from the
    // /auth/refresh endpoint, which refreshes access
    // tokens allowing us to extend our session.
    // It could be desirable for security (especially
    // when editing information becomes a factor) to
    // only refresh tokens when access is proactively
    // granted by the application.
    const { get } = APIActions(this.context);
    const { login, username } = await get("/auth/status");
    return this.setState({ login, username });
  };

  requestLoginForm(v = true) {
    return this.setState({ isLoggingIn: v, invalidAttempt: false });
  }

  doLogin = async (data) => {
    const { post } = APIActions(this.context);
    try {
      const res = await post("/auth/login", data);
      const { login, username } = res;
      return this.setState({
        isLoggingIn: false,
        invalidAttempt: false,
        login,
        username,
      });
    } catch (err) {
      return this.setState({
        invalidAttempt: true,
      });
    }
  };

  doLogout = async () => {
    const { post } = APIActions(this.context);
    const { login } = await post("/auth/logout", {});
    return this.setState({
      login,
      username: null,
      isLoggingIn: false,
    });
  };

  render() {
    const { doLogin, doLogout, requestLoginForm } = this;
    const value = { doLogin, doLogout, requestLoginForm, ...this.state };
    return h(AuthContext.Provider, { value }, this.props.children);
  }
}

const useAuth = () => useContext(AuthContext);

export { AuthContext, AuthProvider, useAuth };
