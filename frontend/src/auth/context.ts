import h from "react-hyperscript";
import { StatefulComponent, APIActions } from "@macrostrat/ui-components";
import { APIV2Context } from "~/api-v2";
import { createContext, useContext } from "react";

type GetStatus = { type: "get-status" };
type RequestForm = { type: "request-form"; enabled: boolean };
type LoginData = { username: string; password: string };
type LoginSuccess = { type: "login" } & LoginData;
type LogoutSuccess = { type: "logout" };

type AuthAction = GetStatus | RequestForm | LoginSuccess | LogoutSuccess;

function dispatchMiddleware(dispatch) {
  return async (action) => {
    switch (action.type) {
      case "get-status":
        await unlink(action.file, () => dispatch(action));
        break;

      default:
        return dispatch(action);
    }
  };
}

interface AuthState {
  login: boolean;
  username: string | null;
  isLoggingIn: boolean;
  invalidAttempt: boolean;
}

interface AuthCtx extends AuthState {
  dispatch(action: AuthAction): void;
}

const authDefaultState: AuthState = {
  login: false,
  username: null,
  isLoggingIn: false,
  invalidAttempt: false,
};

const AuthContext = createContext<AuthCtx>({
  ...authDefaultState,
  dispatch() {},
});

function authReducer(state = authDefaultState, action: AuthAction) {
  switch (action.type) {
    case "get-status":
  }
  return state;
}

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
