import {Component} from 'react'
import h from 'react-hyperscript'
import ReactJson from 'react-json-view'
import {Button, Intent} from '@blueprintjs/core'
import {nullIfError, Argument} from './utils'

class APIUsageComponent extends Component
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

export {APIUsageComponent}
