/*
 * decaffeinate suggestions:
 * DS001: Remove Babel/TypeScript constructor workaround
 * DS102: Remove unnecessary code created because of implicit returns
 * DS206: Consider reworking classes to avoid initClass
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import {Component} from 'react';
import h from 'react-hyperscript';
import {get} from 'axios';
import {Link, Route} from 'react-router-dom';
import ReactJson from 'react-json-view';
import update from 'immutability-helper';
import ReactMarkdown from 'react-markdown';
import styled from '@emotion/styled';
import {StatefulComponent, LinkCard,
        APIContext, APIResultView} from '@macrostrat/ui-components';
import {Colors, Button, Text, AnchorButton, Intent, Icon} from '@blueprintjs/core';
import {join} from 'path';
import {nullIfError, Argument} from './utils';
import {APIUsageComponent} from './usage-component';
import {APIDataComponent} from './data-component';

const Description = styled(ReactMarkdown)`\
font-size: 1.2em;
margin 0.5em 0.2em 1em;\
`;

class RouteName extends Component {
  static initClass() {
    this.contextType = APIContext;
  }
  render() {
    const {baseURL} = this.context;
    let {api_route, queryString, route, parent} = this.props;
    let text = api_route;
    let backLink = h('span.home-icon', [
      h(Icon, {icon: 'home'})
    ]);
    if (queryString == null) { queryString = ""; }
    if (parent != null) {
      text = route;
      // Have to assemble the button ourselves to make it a react-router link
      backLink = h(Link, {
        to: parent,
        className: 'bp3-button bp3-minimal bp3-intent-primary route-parent',
        role: 'button'
      }, [
        h(Icon, {icon: 'arrow-left'}),
        h('span.bp3-button-text', api_route.replace(route, ''))
      ]);
    }
    return h('h2.route-name', [
      backLink,
      h('span.current-route', text),
      h(Text, {ellipsize: true, className: 'query-string'}, queryString),
      h(AnchorButton, {minimal: true, icon: 'link', href: baseURL+route+queryString})
    ]);
  }
}
RouteName.initClass();

const StyledLinkCard = styled(LinkCard)`\
color: ${Colors.BLUE1}\
`;

const ChildRoutesList = function({base, routes}){
  if (routes == null) { return null; }
  return h('div.child-routes', [
    h('h3', 'Routes'),
    h('ul.routes', routes.map(function(d){
      const to = join(base, d.route);
      return h('li.route', [
        h(StyledLinkCard, {to}, [
          h('h4', d.route),
          h('p', d.description)
        ])
      ]);}))
  ]);
};

class RouteComponent extends StatefulComponent {
  static initClass() {
    this.contextType = APIContext;
    this.defaultProps = {
      parent: null
    };
  
    this.prototype.renderSubRoutes = nullIfError(function() {
      const {response} = this.state;
      const {routes} = response;
      const {path: parent} = this.props.match;
      // Use a render function instead of a component match
      const render = props => h(RouteComponent, {...props, parent});
  
      return routes.map(function(r){
        const path = join(parent, r.route);
        return h(Route, {path, key: r.route, render});});});
  }
  constructor(props){
    {
      // Hack: trick Babel/TypeScript into allowing this before super.
      if (false) { super(); }
      let thisFn = (() => { return this; }).toString();
      let thisName = thisFn.match(/return (?:_assertThisInitialized\()*(\w+)\)*;/)[1];
      eval(`${thisName} = this;`);
    }
    this.updateParams = this.updateParams.bind(this);
    this.expandParameter = this.expandParameter.bind(this);
    this.renderMatch = this.renderMatch.bind(this);
    super(props);
    this.state = {
      response: null,
      expandedParameter: null,
      queryString: "",
      params: {}
    };
    this.getData();
  }

  updateParams(cset){
    const {helpers: {buildQueryString}} = this.context;
    const {params} = this.state;
    const newParams = update(params, cset);
    const queryString = buildQueryString(newParams);
    return this.updateState({
      queryString: {$set: queryString},
      params: {$set: newParams}
    });
  }

  routeData() {
    const {parent} = this.props;
    const response = this.state.response || {};
    const api_route = this.apiPath();
    return {parent, api_route, ...response};
  }

  expandParameter(id){
    return this.updateState({expandedParameter: {$set: id}});
  }

  hasSubRoutes() {
    const {routes} = this.state.response || {};
    return (routes || []).length > 0;
  }

  renderMatch() {
    const {response, showJSON, params, queryString} = this.state;
    const {match, parent} = this.props;
    const {path, isExact} = match;
    const exact = this.hasSubRoutes();
    if (response == null) { return null; }
    if (!isExact) { return null; }
    const data = this.routeData();
    const {api_route, route} = data;

    return h(Route, {path, exact}, [
      h('div.route-ui', [
        h('div.panel-header', [
          h(RouteName, {api_route, route, parent, queryString})
        ]),
        h('div.route-body', [
          this.renderBody()
        ])
      ])
    ]);
  }

  renderBody() {
    const data = this.routeData();
    const {params, response, expandedParameter} = this.state;
    const {routes} = response;
    const {path: base} = this.props.match;
    let api_route = this.apiPath();
    if ((data.arguments == null)) {
      // Basically, tell the data component not to render
      api_route = null;
    } else {
      api_route = api_route.replace("/api/v1","");
    }

    return h('div', [
      h(Description, {className: 'description', source: data.description}),
      h(ChildRoutesList, {base, routes}),
      h(APIUsageComponent, {
        data,
        expandedParameter,
        params,
        updateParameters: this.updateParams,
        expandParameter: this.expandParameter
      }),
      h(APIDataComponent, {
        route: api_route,
        params,
        title: "Data",
        storageID: 'data'
      })
    ]);
  }


  render() {
    return h('div', [
      this.renderMatch(),
      this.renderSubRoutes()
    ]);
  }

  apiPath() {
    const {path} = this.props.match;
    return join('/api', path.replace("/api-explorer",""));
  }

  async getData() {
    const {path} = this.props.match;
    // This is a really breakable pattern
    const uri = join(process.env.BASE_URL,this.apiPath(),"/");
    const {data, status} = await get(uri);
    return this.setState({response: data});
  }
}
RouteComponent.initClass();

export {RouteComponent};
