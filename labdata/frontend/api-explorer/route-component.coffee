import {Component} from 'react'
import h from 'react-hyperscript'
import {get} from 'axios'
import {Link, Route} from 'react-router-dom'
import ReactJson from 'react-json-view'

class RouteComponent extends Component
  constructor: (props)->
    super props
    @state = {
      response: null
    }
    @getData()

  renderRoutesList: ->
    try
      {routes} = @state.response
      routes ?= []
    catch
      return null

    h 'ul.routes', routes.map (d)->
      h 'li.route', [
        h Link, {to: d.route}, d.route
      ]

  hasSubRoutes: ->
    {routes} = @state.response or {}
    (routes or []).length > 0

  renderInner: ->
    {response} = @state
    {path} = @props.match
    exact = @hasSubRoutes()
    return null unless response?
    h Route, {path, exact}, [
      h 'div', [
        @renderRoutesList()
        h ReactJson, {src: response}
      ]
    ]

  renderSubRoutes: ->
    r = @state.response
    return null unless r?
    {routes} = r
    return null unless routes?
    routes.map (r)->
      path = r.route
      h Route, {path, key: path, component: RouteComponent}


  render: ->
    console.log @props.match
    console.log @props.location
    h 'div', [
      @renderInner()
      @renderSubRoutes()
    ]

  getData: ->
    {path} = @props.match
    return unless path?
    return if @state.response?
    apiPath = "/api/v1#{path}/describe"
    {data, status} = await get(apiPath)
    @setState {response: data}

export {RouteComponent}
