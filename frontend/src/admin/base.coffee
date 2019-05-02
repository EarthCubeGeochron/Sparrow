import h from 'react-hyperscript'
import {Component} from 'react'
import {Button, ButtonGroup, Icon} from '@blueprintjs/core'
import {Route, Switch} from 'react-router-dom'
import cfg from 'site-content/variables'
import classNames from 'classnames'

import {ProjectListComponent} from './project-component'
import {SessionListComponent} from './session-list-component'
import {AgeChartComponent} from './age-component'
import {SessionComponent} from './session-component'
import {AppNavbar, NavButton} from 'app/shared/navbar'

AdminNavbar = ({base, rest...})->
  h AppNavbar, {rest, subtitle: 'Admin'}, [
    h NavButton, {to: base, icon: 'home'}
    h NavButton, {to: base+'/session'}, "Data"
    h NavButton, {to: base+'/project'}, "Projects"
  ]

SessionMatch = ({match})->
  {id} = match.params
  h SessionComponent, {id}

class AdminBase extends Component
  render: ->
    {match} = @props
    base = match.path
    h 'div#labdata-admin', [
      h AdminNavbar, {base}
      h Switch, [
        h Route, {
          path: base+"/session/:id"
          component: SessionMatch
        }
        h Route, {
          path: base+"/session"
          component: SessionListComponent
        }
        h Route, {
          path: base+"/project"
          component: ProjectListComponent
        }
        h Route, {
          path: base
          component: AgeChartComponent
          exact: true
        }
      ]
    ]

export {AdminBase}
