/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import '../shared/ui-init';

import React from "react";
import {render} from 'react-dom';
import { Route, Link, Redirect } from "react-router-dom";
import h from 'react-hyperscript';

import {RouteComponent} from './route-component';

import './main.styl';

const APIExplorer = function(props){
  const {match} = props;
  return h('div', [
    h('div#api', [
      h(Route, {
        path: `${match.url}`,
        exact: true,
        render() { return h(Redirect, {to: `${match.url}/v1`}); }
      }),
      h(Route, {path: `${match.url}/v1`, component: RouteComponent})
    ])
  ]);
};

export {APIExplorer};
