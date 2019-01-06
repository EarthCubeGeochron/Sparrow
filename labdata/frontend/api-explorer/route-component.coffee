import {Component} from 'react'
import h from 'react-hyperscript'
import {get} from 'axios'
import {Link, Route} from 'react-router-dom'
import ReactJson from 'react-json-view'
import {Button, Intent} from '@blueprintjs/core'
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
  h 'div.argument.bp3-card', {key: name}, [
    h 'h5.name', [
      name+" "
      h 'span.type.bp3-code', type
    ]
    h('p.description', description) if description?
    h('p.default', "Default: #{defaultArg}") if defaultArg?
  ]

class APIUsage extends Component
  @defaultProps: {data: null}
  constructor: (props)->
    super props
    @state = {showJSON: true}

  renderArguments: nullIfError ->
    {arguments: args} = @props.data
    h 'div.arguments', [
      h 'h3', 'Arguments'
      h 'ul.arguments', args.map (d)->
        h 'li', null, (
          h Argument, d
        )
    ]

  renderRecordRoute: nullIfError ->
    {record, api_route} = @props.data
    {route, key: name, type} = record
    route = join api_route, route
    return h 'div.record', [
      h 'h3', route
      h 'p.description', 'Get a single record'
      h Argument, {name, type}
    ]

  render: ->
    {data} = @props
    {showJSON} = @state
    onClick = =>
      @setState {showJSON: not showJSON}

    h 'div.usage', [
      h 'h2', 'Usage'
      h Button, {className: 'toggle-json', onClick}, if showJSON then 'Show summary' else 'Show JSON'
      if showJSON then (
        h ReactJson, {src: data}
      ) else [
        @renderArguments()
        @renderRecordRoute()
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
        h APIUsage, {data}
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
