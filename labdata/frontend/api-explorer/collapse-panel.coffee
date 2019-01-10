# This component should be refactored into a shared UI component

import {Component} from 'react'
import h from 'react-hyperscript'
import {Button, Collapse} from '@blueprintjs/core'
import ReactJson from 'react-json-view'

import {JSONToggle} from './utils'

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
    {title, children, storageID, headerRight, props...} = @props
    {isOpen} = @state

    icon = if isOpen then 'collapse-all' else 'expand-all'
    onClick = => @setState {isOpen: not isOpen}

    headerRight ?= null

    h 'div.collapse-panel', props, [
      h 'div.panel-header', [
        h Button, {icon, minimal: true, onClick}
        h 'h2', title
        h 'div.expander'
        headerRight
      ]
      h Collapse, {isOpen}, children
    ]

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
