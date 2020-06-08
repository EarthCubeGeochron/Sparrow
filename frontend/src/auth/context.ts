/*
 * decaffeinate suggestions:
 * DS001: Remove Babel/TypeScript constructor workaround
 * DS102: Remove unnecessary code created because of implicit returns
 * DS206: Consider reworking classes to avoid initClass
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import h from 'react-hyperscript';
import {APIContext, StatefulComponent} from '@macrostrat/ui-components';
import {createContext, useContext} from 'react';

const AuthContext = createContext({});

class AuthProvider extends StatefulComponent {
  static initClass() {
    this.contextType = APIContext;
  }
  constructor(props){
    super(props);
    this.requestLoginForm = this.requestLoginForm.bind(this);
    this.render = this.render.bind(this);
    this.state = {
      login: false,
      username: null,
      isLoggingIn: false,
      invalidAttempt: false
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
    const {get} = this.context;
    const {login, username} = await get('/auth/status');
    return this.setState({login, username});
  };

  requestLoginForm(v){
    console.log("Requesting login form");
    if (v == null) { v = true; }
    return this.setState({isLoggingIn: v});
  }

  doLogin = async data=> {
    const {post} = this.context;
    const {login, username} = await post('/auth/login', data);
    let invalidAttempt = false;
    let isLoggingIn = false;
    if (!login) {
      invalidAttempt = true;
      isLoggingIn = true;
    }
    return this.setState({
      login,
      username,
      isLoggingIn,
      invalidAttempt
    });
  };

  doLogout = async () => {
    const {post} = this.context;
    const {login} = await post('/auth/logout', {});
    return this.setState({
      login,
      username: null,
      isLoggingIn: false
    });
  };

  render() {
    const methods = (() => { let doLogin, doLogout, requestLoginForm;
    return ({doLogin, doLogout, requestLoginForm} = this); })();
    const value = {...methods, ...this.state};
    return h(AuthContext.Provider, {value}, this.props.children);
  }
}
AuthProvider.initClass();

const useAuth = () => useContext(AuthContext);

export {AuthContext, AuthProvider, useAuth};
