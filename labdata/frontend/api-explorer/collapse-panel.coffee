# This component should be refactored into a shared UI component

import {Component} from 'react'
import h from 'react-hyperscript'
import {Button, Collapse} from '@blueprintjs/core'

class CollapsePanel extends Component
  @defaultProps: {title: "Panel"}
  constructor: (props)->
    super props
    @state = {isOpen: false}

  render: ->
    {title, children, props...} = @props
    {isOpen} = @state
    icon = if isOpen then 'collapse-all' else 'expand-all'
    onClick = => @setState {isOpen: not isOpen}

    h 'div.collapse-panel', props, [
      h 'div.panel-header', [
        h Button, {icon, minimal: true, onClick}
        h 'h2', title
      ]
      h Collapse, {isOpen}, children
    ]

export {CollapsePanel}
