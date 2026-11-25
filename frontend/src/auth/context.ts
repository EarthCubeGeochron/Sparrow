import h from "@macrostrat/hyper";
import { useAPIActions } from "@macrostrat/ui-components";
import { APIV2Context } from "~/api-v2";
import { createContext, useContext, useEffect, useReducer } from "react";
import { readStoredToken, storeToken, tokenFromCookie } from "./token";

type RequestForm = { type: "request-form"; enabled?: boolean };
type Credentials = { username: string; password: string };
type LoginStatus = {
  username: string;
  login: boolean;
  error: Error | null;
  token: string | null;
  orcid?: OrcidSignIn | null;
};

/** Whether the lab offers ORCID sign-in, from /auth/status */
type OrcidSignIn = {
  enabled: boolean;
  mode: "direct" | "broker" | null;
};

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

async function findToken(post): Promise<string | null> {
  /** A token for PostgREST, for a user who signed in before this page loaded */
  const token = readStoredToken() ?? tokenFromCookie();
  if (token != null) return token;
  try {
    // Refreshing re-issues the access cookie with the role claim PostgREST needs
    await post("/auth/refresh", {}, { handleError: false });
  } catch {
    return null;
  }
  return tokenFromCookie();
}

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
          const { login, username, orcid = null } = await get("/auth/status");
          const token = login ? await findToken(post) : null;
          storeToken(token);
          return dispatch({
            type: "update-status",
            payload: { login, username, token, orcid, error: null },
          });
        } catch (error) {
          return dispatch({ type: "update-status", payload: { error } });
        }
      case "login":
        try {
          const res = await post("/auth/login", action.payload);
          const { login, username, token = null } = res;
          storeToken(token);
          return dispatch({
            type: "auth-form-success",
            payload: { username, login, token, error: null },
          });
        } catch (error) {
          return dispatch({
            type: "auth-form-failure",
            payload: { login: false, username: null, token: null, error },
          });
        }
      case "logout": {
        const { login } = await post("/auth/logout", {});
        storeToken(null);
        return dispatch({
          type: "auth-form-success",
          payload: {
            login,
            username: null,
            token: null,
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
  /** JWT sent to PostgREST; null reads data as the public */
  token: string | null;
  orcid: OrcidSignIn | null;
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
  token: readStoredToken(),
  orcid: null,
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
        orcid: state.orcid,
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
