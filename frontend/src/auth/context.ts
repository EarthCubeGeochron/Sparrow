import h from "@macrostrat/hyper";
import { useAPIActions } from "@macrostrat/ui-components";
import { APIV2Context } from "~/api-v2";
import { createContext, useContext, useEffect, useReducer } from "react";

type RequestForm = { type: "request-form"; enabled?: boolean };
type Credentials = { username: string; password: string };
type LoginStatus = { username: string; login: boolean; error: Error | null };

type UpdateStatus = {
  type: "update-status";
  payload: LoginStatus;
};
type AuthSuccess = {
  type: "auth-form-success";
  payload: LoginStatus;
};

type AuthFailure = { type: "auth-form-failure"; payload: LoginStatus };

type AuthAction = RequestForm | UpdateStatus | AuthSuccess | AuthFailure;

type GetStatus = { type: "get-status" };
type Login = { type: "login"; payload: Credentials };
type Logout = { type: "logout" };

type AsyncAuthAction = GetStatus | Login | Logout;

function useAuthActions(dispatch) {
  const { get, post } = useAPIActions(APIV2Context);
  return async (action: AuthAction | AsyncAuthAction) => {
    switch (action.type) {
      case "get-status":
        // Right now, we get login status from the
        // /auth/refresh endpoint, which refreshes access
        // tokens allowing us to extend our session.
        // It could be desirable for security (especially
        // when editing information becomes a factor) to
        // only refresh tokens when access is proactively
        // granted by the application.
        try {
          const { login, username } = await get("/auth/status");
          return dispatch({
            type: "update-status",
            payload: { login, username, error: null },
          });
        } catch (error) {
          return dispatch({ type: "update-status", payload: { error } });
        }
      case "login":
        try {
          const res = await post("/auth/login", action.payload);
          const { login, username } = res;
          return dispatch({
            type: "auth-form-success",
            payload: { username, login, error: null },
          });
        } catch (error) {
          return dispatch({
            type: "auth-form-failure",
            payload: { login: false, username: null, error },
          });
        }
      case "logout": {
        const { login } = await post("/auth/logout", {});
        return dispatch({
          type: "auth-form-success",
          payload: {
            login,
            username: null,
            error: null,
          },
        });
      }
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
  error: Error | null;
}

interface AuthCtx extends AuthState {
  runAction(action: AuthAction | AsyncAuthAction): Promise<void>;
}

const authDefaultState: AuthState = {
  login: false,
  username: null,
  isLoggingIn: false,
  invalidAttempt: false,
  error: null,
};

const AuthContext = createContext<AuthCtx>({
  ...authDefaultState,
  async runAction() {},
});

function authReducer(state = authDefaultState, action: AuthAction) {
  switch (action.type) {
    case "update-status": {
      return {
        ...state,
        ...action.payload,
      };
    }
    case "auth-form-success": {
      return {
        ...action.payload,
        isLoggingIn: false,
        invalidAttempt: false,
      };
    }
    case "auth-form-failure":
      return {
        ...state,
        ...action.payload,
        isLoggingIn: true,
        invalidAttempt: true,
      };
    case "request-form":
      return {
        ...state,
        isLoggingIn: action.enabled ?? true,
        invalidAttempt: false,
      };
    default:
      return state;
  }
}

function AuthProvider(props) {
  const [state, dispatch] = useReducer(authReducer, authDefaultState);
  const runAction = useAuthActions(dispatch);
  useEffect(() => {
    runAction({ type: "get-status" });
  }, []);
  return h(
    AuthContext.Provider,
    { value: { ...state, runAction } },
    props.children
  );
}

const useAuth = () => useContext(AuthContext);

export { AuthContext, AuthProvider, useAuth };
