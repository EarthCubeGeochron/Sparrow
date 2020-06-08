/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS206: Consider reworking classes to avoid initClass
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import {Component} from 'react';
import h from 'react-hyperscript';
import {Button, Intent, Collapse, NonIdealState} from '@blueprintjs/core';
import {Parameter} from './parameter';
import {join} from 'path';
import {JSONCollapsePanel} from './collapse-panel';

class APIUsageComponent extends Component {
  static initClass() {
    this.defaultProps = {data: null};
  }
  constructor(props){
    super(props);
  }

  renderContent() {
    const {expandParameter, updateParameters, params, expandedParameter, data} = this.props;
    const {arguments: args, record, api_route} = data;
    let {route, key: name, type} = record;
    route = join(api_route, route);
    return [
      h('div.arguments', [
        h('p', "Click a parameter to adjust"),
        h('div.arguments-list', args.map(function(d){
          const update = updateParameters;
          const value = params[d.name] || null;
          const expanded = (d.name === expandedParameter) || (value != null);
          return h(Parameter, {expanded, update, value, expand: expandParameter, ...d});}))
      ]),
      h('div.record', [
        h('h3', route),
        h('p.description', 'Get a single record'),
        h(Parameter, {name, type})
      ])
    ];
  }

  renderInterior() {
    try {
      return this.renderContent();
    } catch (err) {
      return h(NonIdealState, {
        title: "No usage information",
        description: "This route does not return data."
      });
    }
  }

  render() {
    const {data} = this.props;
    if (data.arguments == null) { return null; }
    return h(JSONCollapsePanel, {
      data,
      storageID: 'usage',
      className: 'usage',
      title: 'Parameters'
    }, this.renderInterior());
  }
}
APIUsageComponent.initClass();

export {APIUsageComponent};
