import {Component} from 'react'
import h from 'react-hyperscript'
import ReactJson from 'react-json-view'
import {Button, Intent, Collapse} from '@blueprintjs/core'
import {nullIfError, Argument} from './utils'

class APIUsageComponent extends Component
  @defaultProps: {data: null}
  constructor: (props)->
    super props
    @state = {showJSON: true, isOpen: false}

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

  expandButton: ->
    {isOpen} = @state
    icon = if isOpen then 'collapse-all' else 'expand-all'
    onClick = => @setState {isOpen: not isOpen}
    h Button, {icon, minimal: true, onClick}

  render: ->
    {data} = @props
    {showJSON, isOpen} = @state
    onClick = =>
      @setState {showJSON: not showJSON}

    h 'div.usage.collapse-panel', [
      h 'div.panel-header', [
        @expandButton()
        h 'h2', 'Usage'
        h 'div.expander'
        h Button, {
          rightIcon: 'list',
          minimal: true,
          className: 'show-json',
          intent: if not showJSON then Intent.PRIMARY else null
          onClick: => @setState {showJSON: false}
        }, 'Summary'
        h Button, {
          rightIcon: 'code',
          minimal: true,
          className: 'show-json',
          intent: if showJSON then Intent.PRIMARY else null
          onClick: => @setState {showJSON: true}
        }, 'JSON'
      ]
      h Collapse, {isOpen}, (
        if showJSON then (
          h ReactJson, {src: data}
        ) else [
          @renderArguments()
          @renderRecordRoute()
        ]
      )
    ]

export {APIUsageComponent}
