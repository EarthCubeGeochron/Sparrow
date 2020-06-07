/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import h from 'react-hyperscript';
import {Component} from 'react';
import {join} from 'path';
import { BrowserRouter as Router, Route, Switch, useLocation} from "react-router-dom";
import {HomePage} from './homepage';

import siteContent from 'site-content';
import {FrameProvider} from './frame';
import {Intent} from '@blueprintjs/core';
import {APIProvider} from '@macrostrat/ui-components';
import {APIExplorer} from './api-explorer';
import {PageFooter} from './shared/footer';
import {AuthProvider} from './auth';
import {AppToaster} from './toaster';
import {Catalog, CatalogNavLinks} from './admin';
import {AppNavbar, NavButton} from './components/navbar';
import {MapPage} from './map';
import styled from '@emotion/styled';

const AppHolder = styled.div`\
display: flex;
flex-direction: column;
min-height: 100vh;\
`;

const Expander = styled.div`\
flex-grow: 1;\
`;

const GlobalUI = function(props){
  /*
  Defines a hideable global UI component
  */
  const location = useLocation();
  const hidePaths = ['/map'];
  if (hidePaths.includes(location.pathname)) { return null; }
  return h([
    props.children
  ]);
};

const MainNavbar = props => h(AppNavbar, {fullTitle: true}, [
  h(CatalogNavLinks, {base: '/catalog'}),
  h(NavButton, {to: '/map'}, "Map"),
  h(AppNavbar.Divider),
  h(NavButton, {to: '/api-explorer/v1'}, "API")
]);

class AppMain extends Component {
  render() {
    const {baseURL} = this.props;
    return h(Router, {basename: baseURL}, (
      h(AppHolder, [
        h(Expander, [
          h(GlobalUI, null, (
            h(MainNavbar)
          )),
          h(Switch, [
            h(Route, {
              path: '/',
              exact: true,
              render() { return h(HomePage); }
            }),
            h(Route, {
              path: '/catalog',
              render() { return h(Catalog, {base: '/catalog'}); }
            }),
            h(Route, {
              path: '/map',
              component: MapPage
            }),
            h(Route, {path: '/api-explorer', component: APIExplorer})
          ])
        ]),
        h(GlobalUI, null, (
          h(PageFooter)
        ))
      ])
    )
    );
  }
  componentDidMount() {
    const labname = process.env.SPARROW_LAB_NAME;
    return document.title = (labname != null) ? `${labname} – Sparrow` : "Sparrow";
  }
}

const errorHandler = function(route, response){
  let msg;
  const {error} = response;
  if (error != null) {
    msg = error.message;
  }
  const message = h('div.api-error', [
    h('code.bp3-code', route),
    h('p', msg)
  ]);
  return AppToaster.show({message, intent: Intent.DANGER});
};

const App = function() {
  const baseURL = process.env.BASE_URL || "/";
  const apiBaseURL = join(baseURL,'/api/v1');
  console.log(apiBaseURL);

  return h(FrameProvider, {overrides: siteContent}, (
    h(APIProvider, {baseURL: apiBaseURL, onError: errorHandler}, (
      h(AuthProvider, null, (
        h(AppMain, {baseURL})
      ))
    ))
  )
  );
};

export {App};
