/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import {Component} from 'react';
import h from 'react-hyperscript';
import {Route, Switch} from 'react-router-dom';
import {SamplePage} from './page';
import {SampleList} from './list';

class SampleMain extends Component {
  render() {
    const {match} = this.props;
    const base = match.path;
    // Render main body
    return h(Switch, [
      h(Route, {
        path: base+"/:id",
        component: SamplePage
      }),
      h(Route, {
        path: base,
        component: SampleList,
        exact: true
      })
    ]);
  }
}

export {SampleMain, SamplePage, SampleList};
export * from './detail-card';
