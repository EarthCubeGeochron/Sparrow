import {Component} from 'react'
import h from 'react-hyperscript'
import {get} from 'axios'
import {Link, Route} from 'react-router-dom'
import ReactJson from 'react-json-view'
import {join} from 'path'

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
    {match, parent} = @props
    parent ?= null
    {path, isExact} = match
    exact = @hasSubRoutes()
    return null unless response?
    return null unless isExact
    h Route, {path, exact}, [
      h 'div', [
        @renderRoutesList()
        h ReactJson, {src: {parent, response...}}
      ]
    ]

  renderSubRoutes: ->
    {response} = @state
    return null unless response?
    {routes, route} = response
    return null unless routes?
    # Use a render function instead of a component match
    render = (props)->
      h RouteComponent, {props..., parent: route}

    routes.map (r)->
      path = r.route
      h Route, {path, key: path, render}


  render: ->
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
