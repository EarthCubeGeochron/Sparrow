# This component should be refactored into a shared UI component

import {Component} from 'react'
import h from 'react-hyperscript'
import ReactJson from 'react-json-view'

import {CollapsePanel} from '@macrostrat/ui-components'
import {JSONToggle} from './utils'

class JSONCollapsePanel extends Component
  constructor: (props)->
    super props
    @state = {showJSON: false}
  renderInterior: ->
    {showJSON} = @state
    {data, children} = @props
    data ?= {}
    if showJSON
      return h ReactJson, {src: data}
    return h 'div', null, children

  render: ->
    {children, props...} = @props
    {showJSON} = @state
    onChange = (d)=>@setState(d)
    headerRight = h JSONToggle, {showJSON, onChange}
    h CollapsePanel, {props..., headerRight}, @renderInterior()

export {CollapsePanel, JSONCollapsePanel}
