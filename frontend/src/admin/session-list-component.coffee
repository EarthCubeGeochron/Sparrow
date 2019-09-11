import h from 'react-hyperscript'
import {Component} from 'react'
import {Callout, Icon, Card, InputGroup, Menu, MenuItem, Popover, Button, Position} from '@blueprintjs/core'
import {PagedAPIView, StatefulComponent} from '@macrostrat/ui-components'
import {SessionInfoLink} from './session-component/info-card'
import {FilterListComponent} from '../components/filter-list'

SessionListComponent = ->
  route = '/session'
  filterFields = {
    'sample_name': "Sample"
    'project_name': "Project"
    'target': "Material"
    'instrument_name': "Instrument"
    'technique': "Technique"
    'measurement_group_id': 'Group'
  }

  h 'div.data-view#session-list', [
    h Callout, {
      icon: 'info-sign',
      title: "Analytical sessions"
    }, "This page lists analytical sessions (individual instrument runs on a single sample)"
    h FilterListComponent, {
      route,
      filterFields,
      itemComponent: SessionInfoLink
    }
  ]

export {SessionListComponent}
