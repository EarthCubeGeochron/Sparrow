import {Component} from 'react'
import h from 'react-hyperscript'
import {get} from 'axios'
import {Link, Route} from 'react-router-dom'
import ReactJson from 'react-json-view'
import {Button, AnchorButton, Intent, Icon} from '@blueprintjs/core'
import {join} from 'path'
import {nullIfError, Argument} from './utils'
import {APIUsageComponent} from './usage-component'
import {APIDataComponent} from './data-component'

RouteName = ({api_route, route, parent})->
  text = api_route
  if parent?
    text = [
      h AnchorButton, {
        href: join('/api-explorer', parent),
        minimal: true
        intent: Intent.PRIMARY
        className: 'route-parent'
        icon: 'arrow-left'
      }, " "+api_route.replace(route, '')
      h 'span.current-route', route
    ]
  return h 'h2.route-name', text

JSONToggle = ({showJSON, onChange})->
  return [
    h Button, {
      rightIcon: 'list',
      minimal: true,
      className: 'show-json',
      intent: if not showJSON then Intent.PRIMARY else null
      onClick: -> onChange {showJSON: false}
    }, 'Summary'
    h Button, {
      rightIcon: 'code',
      minimal: true,
      className: 'show-json',
      intent: if showJSON then Intent.PRIMARY else null
      onClick: -> onChange {showJSON: true}
    }, 'JSON'
  ]

ChildRoutesList = ({routes})->
  return null unless routes?
  h 'div.child-routes', [
    h 'h3', 'Routes'
    h 'ul.routes', routes.map (d)->
      h 'li.route', [
        h Link, {to: d.route}, (
          h 'div.bp3-card.bp3-interactive', [
            h 'h4', d.route
            h 'p', d.description
          ]
        )
      ]
  ]

class RouteComponent extends Component
  @defaultProps: {
    parent: null
  }
  constructor: (props)->
    super props
    @state = {
      response: null
      showJSON: false
    }
    @getData()

  routeData: ->
    {parent} = @props
    response = @state.response or {}
    api_route = @apiPath()
    {parent, api_route, response...}

  hasSubRoutes: ->
    {routes} = @state.response or {}
    (routes or []).length > 0

  renderMatch: =>
    {response, showJSON} = @state
    {match, parent} = @props
    {path, isExact} = match
    exact = @hasSubRoutes()
    return null unless response?
    return null unless isExact
    data = @routeData()
    {api_route, route} = data

    h Route, {path, exact}, [
      h 'div.route-ui', [
        h 'div.panel-header', [
          h RouteName, {api_route, route, parent}
          h 'div.expander'
          h JSONToggle, {showJSON, onChange: (d)=>@setState(d)}
        ]
        h 'div.route-body', [
          @renderBody()
        ]
      ]
    ]

  renderBody: ->
    {showJSON} = @state

    data = @routeData()
    {routes} = @state.response

    if showJSON
      return h ReactJson, {src: data}
    return [
      h 'p.description', data.description
      h ChildRoutesList, {routes}
      h APIUsageComponent, {data}
      h APIDataComponent, {data}
    ]

  renderSubRoutes: nullIfError ->
    {response} = @state
    {routes} = response
    {path: parent} = @props.match
    # Use a render function instead of a component match
    render = (props)->
      h RouteComponent, {props..., parent}

    routes.map (r)->
      path = r.route
      h Route, {path, key: path, render}


  render: ->
    h 'div', [
      @renderMatch()
      @renderSubRoutes()
    ]

  apiPath: ->
    {path} = @props.match
    join '/api/v1', path

  getData: ->
    {path} = @props.match
    apiPath = join @apiPath(), 'describe'
    {data, status} = await get(apiPath)
    @setState {response: data}

export {RouteComponent}
