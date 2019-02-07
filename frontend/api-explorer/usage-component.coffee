import {Component} from 'react'
import h from 'react-hyperscript'
import {Button, Intent, Collapse, NonIdealState} from '@blueprintjs/core'
import {Parameter} from './parameter'
import {join} from 'path'
import {JSONCollapsePanel} from './collapse-panel'

ParamItem = (d)->
  i = h Parameter, d
  h 'li', null, i

class APIUsageComponent extends Component
  @defaultProps: {data: null}
  constructor: (props)->
    super props

  renderContent: ->
    {expandParameter, expandedParameter, data} = @props
    {arguments: args, record, api_route} = data
    {route, key: name, type} = record
    route = join api_route, route
    return [
      h 'div.arguments', [
        h 'h3', 'Arguments'
        h 'ul.arguments', args.map (d)->
          expanded = d.name == expandedParameter
          h ParamItem, {expanded, expandParameter, d...}
      ]
      h 'div.record', [
        h 'h3', route
        h 'p.description', 'Get a single record'
        h Parameter, {name, type}
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
    return null unless data.arguments?
    h JSONCollapsePanel, {
      data
      storageID: 'usage',
      className: 'usage',
      title: 'Parameters'
    }, @renderInterior()

export {APIUsageComponent}
