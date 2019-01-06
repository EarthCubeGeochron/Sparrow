import {Component} from 'react'
import h from 'react-hyperscript'
import ReactJson from 'react-json-view'
import {Button, Intent, Collapse, NonIdealState} from '@blueprintjs/core'
import {Argument} from './utils'
import {join} from 'path'

class APIUsageComponent extends Component
  @defaultProps: {data: null}
  constructor: (props)->
    super props
    @state = {isOpen: false}

  renderContent: ->
    {arguments: args, record, api_route} = @props.data
    {route, key: name, type} = record
    route = join api_route, route
    return [
      h 'div.arguments', [
        h 'h3', 'Arguments'
        h 'ul.arguments', args.map (d)->
          h 'li', null, (
            h Argument, d
          )
      ]
      h 'div.record', [
        h 'h3', route
        h 'p.description', 'Get a single record'
        h Argument, {name, type}
      ]
    ]

  renderInterior: ->
    try
      return @renderContent()
    catch err
      return h NonIdealState, {
        title: "No usage information"
        description: "This route does not return data."
      }

  expandButton: ->
    {isOpen} = @state
    icon = if isOpen then 'collapse-all' else 'expand-all'
    onClick = => @setState {isOpen: not isOpen}
    h Button, {icon, minimal: true, onClick}

  render: ->
    {data} = @props
    {showJSON, isOpen} = @state

    h 'div.usage.collapse-panel', [
      h 'div.panel-header', [
        @expandButton()
        h 'h2', 'Usage'
      ]
      h Collapse, {isOpen}, @renderInterior()
    ]

export {APIUsageComponent}
