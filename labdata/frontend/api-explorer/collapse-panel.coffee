# This component should be refactored into a shared UI component

import {Component} from 'react'
import h from 'react-hyperscript'
import {Button, Collapse} from '@blueprintjs/core'

class CollapsePanel extends Component
  @defaultProps: {
    title: "Panel"
    # `storageID` prop allows storage of state in
    # localStorage or equivalent.
    storageID: null
  }
  constructor: (props)->
    super props

  componentWillMount: ->
    # Set open state from local storage if it is available
    {storageID} = @props
    return unless storageID?
    isOpen = @savedState()[storageID]
    return unless isOpen?
    @setState {isOpen}

  ###
  Next functions are for state management
  across pages, if storageID prop is passed
  ###
  savedState: ->
    st = window.localStorage.getItem('collapse-panel-state')
    try
      return JSON.parse(st)
    catch
      return {}

  checkLocalStorage: ->
    # Set open state from local storage if it is available
    {storageID} = @props
    return unless storageID?
    isOpen = @savedState()[storageID] or null
    isOpen ?= false
    @setState {isOpen}

  componentDidUpdate: (prevProps, prevState)->
    # Refresh object in local storage
    {storageID} = @props
    return unless storageID?
    {isOpen} = @state
    return unless isOpen != prevState.isOpen
    s = @savedState()
    s[storageID] = isOpen
    j = JSON.stringify(s)
    window.localStorage.setItem('collapse-panel-state', j)

  render: ->
    {title, children, storageID, props...} = @props
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
