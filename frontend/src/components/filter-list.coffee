import h from 'react-hyperscript'
import {Component} from 'react'
import {
  Callout, Icon, Card, InputGroup,
  Menu, MenuItem, Popover,
  Button, Position} from '@blueprintjs/core'
import {PagedAPIView, StatefulComponent} from '@macrostrat/ui-components'
import T from 'prop-types'

class FilterListComponent extends StatefulComponent
  @propTypes: {
    route: T.string.isRequired
    filterFields: T.objectOf(T.string).isRequired
    itemComponent: T.elementType.isRequired
  }
  constructor: (props)->
    super props
    @state = {
      filter: ''
      field: Object.keys(@props.filterFields)[0]
      isSelecting: false
    }

  updateFilter: (event)=>
    {value} = event.target
    @updateState {filter: {$set: value}}

  render: ->
    {route, filterFields, itemComponent, rest...} = @props
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

    h PagedAPIView, {
      className: 'data-frame'
      extraPagination: filterBox
      params
      route
      topPagination: true
      bottomPagination: true
      perPage: 10
      rest...
    }, (data)->
      h 'div', null, data.map (d)-> h(itemComponent, d)

export {FilterListComponent}
