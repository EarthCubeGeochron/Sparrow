import {Component} from 'react'
import h from 'react-hyperscript'
import {get} from 'axios'
import {Link, Route} from 'react-router-dom'
import ReactJson from 'react-json-view'
import {join} from 'path'

nullIfError = (fn)-> ->
  # Returns null if the function returns an
  # error...useful for creating React component trees
  try
    return fn.apply(@, arguments)
  catch error
    console.log "Ignored '#{error}'', returning null"
    return null

Argument = (props)->
  {name, type, default: defaultArg, description} = props
  console.log name, type
  h 'div.argument', {key: name}, [
    h 'h5.name', [
      name+" "
      h 'span.type', type
    ]

    h('p.description', description) if description?
    h('p.default', "Default: #{defaultArg}") if defaultArg?
  ]

class RouteComponent extends Component
  @defaultProps: {
    parent: null
  }
  constructor: (props)->
    super props
    @state = {
      response: null
    }
    @getData()

  renderRoutesList: nullIfError ->
    {routes} = @state.response
    h 'div.child-routes', [
      h 'h4', 'Child routes'
      h 'ul.routes', routes.map (d)->
        h 'li.route', [
          h Link, {to: d.route}, (
            h 'div', [
              h 'h5', d.route
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
    {response} = @state
    {match, parent} = @props
    {path, isExact} = match
    exact = @hasSubRoutes()
    return null unless response?
    return null unless isExact
    data = @routeData()

    h Route, {path, exact}, [
      h 'div', [
        h 'div.basic-info', [
          h 'h2.route-name', data.api_route
          h 'p.description', data.description
        ]
        h Link, {to: parent}, "Back to parent" if parent?
        @renderRoutesList()
        @renderArguments()
        @renderRecordRoute()
        h ReactJson, {src: data}
      ]
    ]

  renderArguments: nullIfError ->
    {arguments: args} = @state.response
    h 'div.arguments', [
      h 'h4', 'Arguments'
      h 'ul.arguments', args.map (d)->
        h 'li', null, (
          h Argument, d
        )
    ]

  renderRecordRoute: nullIfError ->
    {record, api_route} = @routeData()
    {route, key: name, type} = record
    route = join api_route, route
    return h 'div.record', [
      h 'h4', route
      h 'p.description', 'Get a single record'
      h Argument, {name, type}
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
