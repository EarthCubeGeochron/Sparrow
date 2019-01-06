import {Component} from 'react'
import h from 'react-hyperscript'
import ReactJson from 'react-json-view'
import {Button, Intent, Collapse, NonIdealState} from '@blueprintjs/core'
import {Argument} from './utils'
import {join} from 'path'
import {CollapsePanel} from './collapse-panel'

class APIUsageComponent extends Component
  @defaultProps: {data: null}
  constructor: (props)->
    super props

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

  render: ->
    {data} = @props
    h CollapsePanel, {className: 'usage', title: 'Usage'}, @renderInterior()

export {APIUsageComponent}
