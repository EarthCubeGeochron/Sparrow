import {Component} from 'react'
import h from 'react-hyperscript'
import {get} from 'axios'
import {Link, Route} from 'react-router-dom'
import ReactJson from 'react-json-view'
import update from 'immutability-helper'
import ReactMarkdown from 'react-markdown'
import styled from '@emotion/styled'
import {StatefulComponent, LinkCard,
        APIContext, APIResultView} from '@macrostrat/ui-components'
import {Colors, Button, Text, AnchorButton, Intent, Icon} from '@blueprintjs/core'
import {join} from 'path'
import {nullIfError, Argument} from './utils'
import {APIUsageComponent} from './usage-component'
import {APIDataComponent} from './data-component'

Description = styled(ReactMarkdown)"""
  font-size: 1.2em;
  margin 0.5em 0.2em 1em;
"""

class RouteName extends Component
  @contextType: APIContext
  render: ->
    {baseURL} = @context
    {api_route, queryString, route, parent} = @props
    text = api_route
    backLink = h 'span.home-icon', [
      h Icon, {icon: 'home'}
    ]
    queryString ?= ""
    if parent?
      text = route
      # Have to assemble the button ourselves to make it a react-router link
      backLink = h Link, {
        to: parent
        className: 'bp3-button bp3-minimal bp3-intent-primary route-parent'
        role: 'button'
      }, [
        h Icon, {icon: 'arrow-left'}
        h 'span.bp3-button-text', api_route.replace(route, '')
      ]
    return h 'h2.route-name', [
      backLink
      h 'span.current-route', text
      h Text, {ellipsize: true, className: 'query-string'}, queryString
      h AnchorButton, {minimal: true, icon: 'link', href: baseURL+route+queryString}
    ]

StyledLinkCard = styled(LinkCard)"""
  color: #{Colors.BLUE1}
"""

ChildRoutesList = ({base, routes})->
  return null unless routes?
  h 'div.child-routes', [
    h 'h3', 'Routes'
    h 'ul.routes', routes.map (d)->
      to = join(base, d.route)
      h 'li.route', [
        h StyledLinkCard, {to}, [
          h 'h4', d.route
          h 'p', d.description
        ]
      ]
  ]

class RouteComponent extends StatefulComponent
  @contextType: APIContext
  @defaultProps: {
    parent: null
  }
  constructor: (props)->
    super props
    @state = {
      response: null
      expandedParameter: null
      queryString: ""
      params: {}
    }
    @getData()

  updateParams: (cset)=>
    {helpers: {buildQueryString}} = @context
    {params} = @state
    newParams = update params, cset
    queryString = buildQueryString newParams
    @updateState {
      queryString: {$set: queryString}
      params: {$set: newParams}
    }

  routeData: ->
    {parent} = @props
    response = @state.response or {}
    api_route = @apiPath()
    {parent, api_route, response...}

  expandParameter: (id)=>
    @updateState {expandedParameter: {$set: id}}

  hasSubRoutes: ->
    {routes} = @state.response or {}
    (routes or []).length > 0

  renderMatch: =>
    {response, showJSON, params, queryString} = @state
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
          h RouteName, {api_route, route, parent, queryString}
        ]
        h 'div.route-body', [
          @renderBody()
        ]
      ]
    ]

  renderBody: ->
    data = @routeData()
    {params, response, expandedParameter} = @state
    {routes} = response
    {path: base} = @props.match
    api_route = @apiPath()
    if not data.arguments?
      # Basically, tell the data component not to render
      api_route = null
    else
      api_route = api_route.replace("/api/v1","")

    return h 'div', [
      h Description, {className: 'description', source: data.description}
      h ChildRoutesList, {base, routes}
      h APIUsageComponent, {
        data
        expandedParameter
        params
        updateParameters: @updateParams
        expandParameter: @expandParameter
      }
      h APIDataComponent, {
        route: api_route
        params
        title: "Data"
        storageID: 'data'
      }
    ]

  renderSubRoutes: nullIfError ->
    {response} = @state
    {routes} = response
    {path: parent} = @props.match
    # Use a render function instead of a component match
    render = (props)->
      h RouteComponent, {props..., parent}

    routes.map (r)->
      path = join parent, r.route
      h Route, {path, key: r.route, render}


  render: ->
    h 'div', [
      @renderMatch()
      @renderSubRoutes()
    ]

  apiPath: ->
    {path} = @props.match
    join '/api', path.replace("/api-explorer","")

  getData: ->
    {path} = @props.match
    {data, status} = await get('/labs/wiscar'+@apiPath()+"/")
    @setState {response: data}

export {RouteComponent}
