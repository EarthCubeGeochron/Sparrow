import h from 'react-hyperscript'
import {Component} from 'react'
import {Callout, Icon, Card, InputGroup, Menu, MenuItem, Popover, Button, Position} from '@blueprintjs/core'
import {PagedAPIView, StatefulComponent} from '@macrostrat/ui-components'
import {SessionInfoLink} from './session-component/info-card'

class SessionListComponent extends StatefulComponent
  @defaultProps: {
    apiEndpoint: '/session'
    filterFields: {
      'sample_id': "Sample"
      'project_name': "Project"
      'target': "Material"
      'instrument_name': "Instrument"
      'technique': "Technique"
      'measurement_group_id': 'Group'
    }
  }
  constructor: (props)->
    super props
    @state = {
      filter: ''
      field: 'sample_id'
      isSelecting: false
    }

  updateFilter: (event)=>
    {value} = event.target
    @updateState {filter: {$set: value}}

  render: ->
    {apiEndpoint, filterFields} = @props
    {filter, field} = @state
    params = {}
    if filter? and filter != ""
      val = "%#{filter}%"
      params = {[field]: val}


    menuItems = []
    onClick = (k)=> => @updateState {
      field: {$set: k}
      filter: {$set: ''}
    }

    for k,v of filterFields
      menuItems.push h Button, {minimal: true, onClick: onClick(k)}, v

    content = h Menu, menuItems
    position = Position.BOTTOM_RIGHT

    rightElement = h Popover, {content, position}, [
      h Button, {minimal: true, rightIcon: "caret-down"}, filterFields[field]
    ]

    filterBox = h InputGroup, {
      leftIcon: 'search'
      placeholder: "Filter values"
      value: @state.filter
      onChange: @updateFilter
      rightElement
    }


    h 'div.data-view#session-list', [
      h Callout, {
        icon: 'info-sign',
        title: "Analytical sessions"
      }, "This page contains the core data view for laboratory analytical data"
      h PagedAPIView, {
        className: 'data-frame'
        extraPagination: filterBox
        params
        route: apiEndpoint
        topPagination: true
        bottomPagination: false
        perPage: 10
      }, (data)->
        h 'div', null, data.map (d)-> h(SessionInfoLink, d)
    ]

export {SessionListComponent}
