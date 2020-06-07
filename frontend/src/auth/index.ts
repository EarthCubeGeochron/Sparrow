/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS206: Consider reworking classes to avoid initClass
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import {hyperStyled} from '@macrostrat/hyper';
import {Component} from 'react';
import {Button} from '@blueprintjs/core';
import {LoginForm} from './login-form';
import {AuthProvider, AuthContext, useAuth} from './context';
import styles from './module.styl';
const h = hyperStyled(styles);

class AuthStatus extends Component {
  static initClass() {
    this.contextType = AuthContext;
  }
  render() {
    const {requestLoginForm, username} = this.context;
    let {className, large, ...rest} = this.props;
    if (large == null) { large = true; }

    let text = 'Not logged in';
    let icon = 'blocked-person';
    if (username != null) {
      text = username;
      icon = 'person';
    }
    return h('div.auth-status', {className}, [
      h(LoginForm),
      h(Button, {
        minimal: true,
        large,
        icon,
        onClick: requestLoginForm}, text)
    ]);
  }
}
AuthStatus.initClass();

export * from './login-form';
export {AuthProvider, AuthStatus, useAuth};
