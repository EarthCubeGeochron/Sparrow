/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import {hyperStyled, classed, addClassNames} from '@macrostrat/hyper';
import {Navbar, Button, ButtonGroup, Icon, Menu, MenuItem} from '@blueprintjs/core';
import {NavLink, Route, Switch} from 'react-router-dom';
import {LinkButton, NavLinkButton} from '@macrostrat/ui-components';

import {AuthStatus} from 'app/auth';
import {Frame} from 'app/frame';
import styles from './module.styl';

const h = hyperStyled(styles);

const NavButton = classed(NavLinkButton, 'navbar-button');

const SiteTitle = () => h(NavLink, {to: '/'}, (
  h(Frame, {id: 'siteTitle'}, "Test Lab")
));

const AppNavbar = function({children, fullTitle, subtitle, ...rest}){
  if (children == null) { children = null; }
  const p = addClassNames(rest, 'app-navbar');
  return h(Navbar, p, [
    h(Navbar.Group, [
      h(Navbar.Heading, [
        h('h1.site-title', null, [
          h(SiteTitle),
          h.if(subtitle != null)([
            h('span', ":"),
            h('span.subtitle', subtitle)
          ])
        ])
      ]),
      h.if(children != null)(Navbar.Divider),
      children,
      h(AuthStatus, {className: 'auth-right'})
    ])
  ]);
};

AppNavbar.Divider = Navbar.Divider;


const MinimalNavbar = props => h('div.minimal-navbar', props);

export {AppNavbar, NavButton, SiteTitle, MinimalNavbar};
