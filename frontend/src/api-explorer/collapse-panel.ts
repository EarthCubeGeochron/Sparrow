/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
// This component should be refactored into a shared UI component

import {Component} from 'react';
import h from 'react-hyperscript';
import ReactJson from 'react-json-view';

import {CollapsePanel} from '@macrostrat/ui-components';
import {JSONToggle} from './utils';

class JSONCollapsePanel extends Component {
  constructor(props){
    super(props);
    this.state = {showJSON: false};
  }
  renderInterior() {
    const {showJSON} = this.state;
    let {data, children} = this.props;
    if (data == null) { data = {}; }
    if (showJSON) {
      return h(ReactJson, {src: data});
    }
    return h('div', null, children);
  }

  render() {
    const {children, ...props} = this.props;
    const {showJSON} = this.state;
    const onChange = d=> this.setState(d);
    const headerRight = h(JSONToggle, {showJSON, onChange});
    return h(CollapsePanel, {...props, headerRight}, this.renderInterior());
  }
}

export {CollapsePanel, JSONCollapsePanel};
