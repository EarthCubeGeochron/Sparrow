import {Component} from 'react'
import h from 'react-hyperscript'
import {get} from 'axios'
import {Link, Route} from 'react-router-dom'
import ReactJson from 'react-json-view'
import {Button, AnchorButton, Intent, Icon} from '@blueprintjs/core'
import {join, basename} from 'path'
import {nullIfError, Argument} from './utils'
import {APIUsageComponent} from './usage-component'
import {APIDataComponent} from './data-component'

RouteName = ({api_route, route, parent})->
  text = api_route
  backLink = h 'span.home-icon', [
    h Icon, {icon: 'home'}
  ]
  if parent?
    text = route
    backLink = [
      # Have to assemble the button ourselves to make it a react-router link
      h Link, {
        to: parent.replace('/api','')
        className: 'bp3-button bp3-minimal bp3-intent-primary route-parent'
        role: 'button'
      }, [
        h Icon, {icon: 'arrow-left'}
        h 'span.bp3-button-text', api_route.replace(route, '')
      ]
    ]
  return h 'h2.route-name', [
    backLink
    h 'span.current-route', text
  ]

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

ChildRoutesList = ({base, routes})->
  return null unless routes?
  h 'div.child-routes', [
    h 'h3', 'Routes'
    h 'ul.routes', routes.map (d)->
      to = join(base, d.route)
      h 'li.route', [
        h Link, {to}, (
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

  componentDidUpdate: (prevProps)->
    return unless prevProps.location != @props.location
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
    {match, location, parent} = @props
    console.log match, location
    {path, isExact} = match
    exact = false #@hasSubRoutes()
    return null unless response?
    data = @routeData()
    {api_route, route} = data
    {pathname} = @props.location
    api_route = '/api'+pathname
    route = "/"+(api_route.replace('/api/v1','').split('/').pop())
    parent = api_route.replace(route,"")
    parent = null if route == '/'

    console.log pathname, api_route, route, parent

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
    {path: base} = @props.match

    if showJSON
      return h ReactJson, {src: data}
    return [
      h 'p.description', data.description
      h ChildRoutesList, {base, routes}
      h APIUsageComponent, {data}
      h APIDataComponent, {data}
    ]

  renderSubRoutes: nullIfError ->
    {response} = @state
    {routes} = response
    {pathname: parent} = @props.location
    console.log parent
    # Use a render function instead of a component match
    render = (props)->
      h RouteComponent, {props..., parent}

    routes.map (r)->
      path = join parent, r.route
      h Route, {path, key: r.route, render}


  render: ->
    h 'div', [
      @renderMatch()
      #@renderSubRoutes()
    ]

  apiPath: ->
    {pathname} = @props.location
    join '/api', pathname

  getData: ->
    apiPath = join @apiPath(), 'describe'
    console.log apiPath
    {data, status} = await get(apiPath)
    @setState {response: data}

export {RouteComponent}
