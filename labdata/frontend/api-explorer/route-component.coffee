import {Component} from 'react'
import h from 'react-hyperscript'
import {get} from 'axios'
import {Link, Route} from 'react-router-dom'
import ReactJson from 'react-json-view'
import {Button, Intent} from '@blueprintjs/core'
import {join} from 'path'
import {nullIfError, Argument} from './utils'
import {APIUsageComponent} from './usage-component'

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

  renderRoutesList: nullIfError ->
    {routes} = @state.response
    h 'div.child-routes', [
      h 'h2', 'Children'
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

  routeData: ->
    {parent} = @props
    response = @state.response or {}
    api_route = @apiPath()
    {parent, api_route, response...}

  hasSubRoutes: ->
    {routes} = @state.response or {}
    (routes or []).length > 0

  renderMatch: ->
    {response, showJSON} = @state
    {match, parent} = @props
    {path, isExact} = match
    exact = @hasSubRoutes()
    return null unless response?
    return null unless isExact
    data = @routeData()

    h Route, {path, exact}, [
      h 'div', [
        h 'div.basic-info', [
          h Link, {to: parent}, "Back to parent" if parent?
          h 'h2.route-name', data.api_route
          h 'p.description', data.description
        ]
        @renderRoutesList()
        h APIUsageComponent, {data}
      ]
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
